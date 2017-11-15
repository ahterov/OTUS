import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import date, time



def get_dfs():
    name = input('Введите название учетную запись facebook(по умолчанию будет выбрана страница телеканала Дождь - tvrain): ')
    if len(name) < 1: name = 'tvrain'
    conn = sqlite3.connect(name + '.sqlite')
    cur = conn.cursor()

    data_post = list()
    bad_word = ['а', 'в', 'и', 'или', 'но', 'на', 'под', 'у', 'к', 'с', 'над', 'от', 'по', 'до', 'да']
    word_count = dict()
    cur.execute('SELECT * FROM Posts')
    for row in cur:
        try: d = date(int(row[2].split('T')[0].split('-')[0]), int(row[2].split('T')[0].split('-')[1]), int(row[2].split('T')[0].split('-')[2]))
        except: d = None
        try: t = time(int(row[2].split('T')[1].split('+')[0].split(':')[0]), int(row[2].split('T')[1].split('+')[0].split(':')[1]))
        except: t = None
        data_post.append({'id': row[0], 'Message': row[1], 'Date': d, 'Time': t, 'Likes': row[3]})

    data_comment = list()
    cur.execute('SELECT * FROM Comments')
    for row in cur:
        try: d = date(int(row[3].split('T')[0].split('-')[0]), int(row[3].split('T')[0].split('-')[1]), int(row[3].split('T')[0].split('-')[2]))
        except: d = None
        try: t = time(int(row[3].split('T')[1].split('+')[0].split(':')[0]), int(row[3].split('T')[1].split('+')[0].split(':')[1]))
        except: t = None
        data_comment.append({'Message_id': row[1], 'Comment': row[2], 'Date': d, 'Time': t})

    return pd.DataFrame(data_post), pd.DataFrame(data_comment)


def main():
    print (
    '''
         ========================================Введение==========================================================
        В ходе визуализации будут построены следующие диаграммы:
        1. Столбчатые диаграммы, показывающие количество постов и комментариев по дням
        2. Диаграмма разброса, показывающая зависимость (или ее отсутствие) количества комментариев от количества постов (каждая точка – 1 день)
        3. Столбчатая диаграмма, показывающая количество реакций пользователей на посты (лайки + остальные эмоции) по дням
        4. Диаграмма разброса, визуализирующая зависимость количества комментариев под постом от количества реакций пользователей (лайки + остальные эмоции) на него
        5. Столбчатые диаграммы, показывающие количество постов и комментариев по временным полуинтервалам (длина интервала - 1 час).
        
        Выводы: 
        1.	Из диаграммы 2 можно сделать странный вывод о том, что чем больше в день делается постов, тем меньше в итоге оказывается комментариев. Что бы проверить необходимо больше данных. 
        2.	Из диаграммы 3 напрашивается один единственный вывод: так как 13 ноября - это понедельник, то можно предположить, что люди вышли на работу и давай комментировать посты
        3.	Из диаграммы 4 видна прямая зависимость между количеством комментариев под постом от количества реакций пользователей на этот пост (в принципе, логично)
        4.	Из диаграммы 5 можно сделать вывод, что больше всего постов делается в интервале от 15:00 до 16:00 и от 17:00 до 18:00. Комментарии же чаще всего оставляют в утренние часы: от 6:00 до 9:00 (перед уходом на работу), а также днем с 15:00 до 16:00. Это если я не напутал с часовым поясом и facebook отдавал мне нужное время, а не свое локальное
        Что можно сделать еще (но не успел): Посмотреть на распределение слов в постах и комментариях, 
        найти наиболее часто используемые слова, взять самые комментируемые и посты, 
        вызвавшие наибольшее кол-во реакций, и сравнить их с наиболее часто используемыми словами. 
        Может быть удастся найти зависимость тематики постов 
        (определить по наиболее употребляемым словам) с предпочтениями пользователей.        
        ======================================================================================================================
        ''')
    df_post, df_comment = get_dfs()
    df1 = df_post.groupby(['Date'])
    df2 = df_comment.groupby(['Date'])

    #============================================================
    fig, ax1 = plt.subplots(2, 1, figsize=(10, 6))
    df1['Message'].size().plot.bar(ax=ax1[0], x='Date', title='Динамика количества постов по дням', color='#9AFE2E',
                                   sharex=True)
    for i, v in enumerate(df1['Message'].size()): ax1[0].text(i - 0.1, v + 1, str(v))
    ax1[0].axes.get_yaxis().set_visible(False)

    df2['Comment'].size().plot.bar(ax=ax1[1], x='Date', title='Динамика количества комментариев по дням',
                                   color='#FE9A2E')
    for i, v in enumerate(df2['Comment'].size()): ax1[1].text(i - 0.1, v + 2, str(v))
    ax1[1].axes.get_yaxis().set_visible(False)
    #============================================================
    df3 = pd.DataFrame({'Count_mess': df1['Message'].size(), 'Count_comm': df2['Comment'].size()})
    fig, ax1 = plt.subplots(1, 1, figsize=(7, 5))
    df3.plot.scatter(ax=ax1, x='Count_mess', y='Count_comm',
                     title='Зависимомть кол-ва комментариев от кол-ва постов (каждая точка - 1 день)')
    ax1.set_xlabel('Кол-во постов (по дням)')
    ax1.set_ylabel('Кол-во комментариев (по дням)')
    #============================================================
    fig, ax1 = plt.subplots(1, 1, figsize=(7, 5))
    df1['Likes'].sum().plot.bar(ax=ax1, x='Date', title='Динамика количества реакций по дням', color='#FFFF00')
    for i, v in enumerate(df1['Likes'].sum()): ax1.text(i - 0.2, v + 3, str(v))
    #============================================================
    df4 = pd.DataFrame({'Count_react': df_post.groupby(['id'])['Likes'].sum(), 'Count_comm': df_comment.groupby(['Message_id'])['Comment'].size()})
    fig, ax1 = plt.subplots(1, 1, figsize=(7, 5))
    df4.plot.scatter(ax=ax1, x='Count_react', y='Count_comm',
                     title='Зависимомть кол-ва комментариев под постом от кол-ва реакций (каждая точка - 1 пост)')
    print(df4.head())
    ax1.set_xlabel('Кол-во комментариев (по постам)')
    ax1.set_ylabel('Кол-во реакций (по постам)')
    # ============================================================
    posts_by_hour = list()
    for hour in range(0,24):
        count = df_post[(df_post.Time >= time(hour, 0)) & (df_post.Time <= time(hour, 59))].shape[0]
        posts_by_hour.append({'Interval': str(hour)+':00-'+str(hour)+':59', 'Count': count})
    df5 = pd.DataFrame(posts_by_hour)

    comments_by_hour = list()
    for hour in range(0,24):
        count = df_comment[(df_comment.Time >= time(hour, 0)) & (df_comment.Time <= time(hour, 59))].shape[0]
        comments_by_hour.append({'Interval': str(hour)+':00-'+str(hour)+':59', 'Count': count})
    df6 = pd.DataFrame(comments_by_hour)

    fig, ax1 = plt.subplots(2, 1, figsize=(10, 6))
    df5.plot.bar(ax=ax1[0], x='Interval', title='Динамика количества постов по часам', color='#9A2EFE',
                                   sharex=True)
    for i, v in enumerate(df5['Count']): ax1[0].text(i - 0.1, v + 1, str(v))
    ax1[0].axes.get_yaxis().set_visible(False)

    df6.plot.bar(ax=ax1[1], x='Interval', title='Динамика количества комментариев по часам',
                                   color='#A4A4A4')
    for i, v in enumerate(df6['Count']): ax1[1].text(i - 0.1, v + 2, str(v))
    ax1[1].axes.get_yaxis().set_visible(False)
    
    plt.show()


if __name__ == '__main__':
    main()