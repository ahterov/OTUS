import keys
import json
import urllib.parse, urllib.request
import sqlite3


def get_url_posts(page_name, param = {}):
    host = 'https://graph.facebook.com/'
    return host + page_name + '/posts/?access_token=' + keys.get_access_token() + urllib.parse.urlencode(param)


def get_url_likes(post_id, param = {}):
    host = 'https://graph.facebook.com/'
    return host + post_id + '/reactions?summary=true&access_token=' + keys.get_access_token() + urllib.parse.urlencode(param)


def get_url_comments(post_id, param = {}):
    host = 'https://graph.facebook.com/'
    return host + post_id + '/comments/?access_token=' + keys.get_access_token() + urllib.parse.urlencode(param)


def get_likes_count(url, message):
    try:
        print('Получаем кол-во лайков поста "' + message[:100] + '..."')
        data = urllib.request.urlopen(url).read().decode()
        json_likes = json.loads(data)
        return json_likes["summary"]["total_count"]
    except:
        print ('При получении кол-ва лайков что-то пошло не так :(')


def get_comments(url, comment_count=1000):
    comments = list()
    try:
        data = urllib.request.urlopen(url).read().decode()
        json_comments = json.loads(data)
        count = comment_count
        for comment in json_comments["data"]:
            comm_id = comment['id']
            comm_message = comment['message']
            com_created_time = comment['created_time']
            comments.append({'id': comm_id, 'comment': comm_message, 'time': com_created_time})
            count -= 1
            if count == 0: return comments
        if (count > 0) and (json_comments["paging"].get('next') is not None):
            comments = comments + get_comments(json_comments["paging"]['next'], comment_count)
    except:
        print ('При получении комментариев что-то пошло не так :(')
    return comments


def get_posts(url, posts, cursor, connection, posts_count=100):
    try:
        print('Получаем посты со страницы. Осталось получить {} постов'.format(posts_count))
        data = urllib.request.urlopen(url).read().decode()
        json_posts = json.loads(data)
        count = posts_count
        for post in json_posts["data"]:
            id = post['id']
            message = post['message']
            created_time = post['created_time']
            likes_count = get_likes_count(get_url_likes(id), message)
            print('Получаем комментарии под постом "' + message[:100] + '..."')
            comments = get_comments(get_url_comments(id))
            posts.append({'id': id, 'message': message, 'time': created_time, 'likes': likes_count, 'comments': comments})
            try:
                cursor.execute('INSERT OR IGNORE INTO Posts (id, message, created_time, likes_count) VALUES (?, ?, ?, ?)',
                               (id, message, created_time, likes_count))
                cursor.execute('UPDATE Posts SET message=?, likes_count=? WHERE id=?',
                               (message, likes_count, id))
                connection.commit()
            except:
                print('При добавлении постов в БД что-то пошло не так :(')
            try:
                for comment in comments:
                    cursor.execute(
                        'INSERT OR IGNORE INTO Comments (id, message_id, comment, created_time) VALUES (?, ?, ?, ?)',
                        (comment['id'], id, comment['comment'], comment['time']))
                    cursor.execute('UPDATE Comments SET comment=? WHERE id=?', (comment['comment'], comment['id']))
                    connection.commit()
            except:
                print('При добавлении комментариев к посту в БД что-то пошло не так :(')
            count -= 1
            if count == 0: return
        if (count > 0) and (json_posts["paging"].get('next') is not None):
            get_posts(json_posts["paging"]['next'], posts, cursor, connection, count)
    except:
        print ('При получении постов что-то пошло не так :(')


#def insert_into_db(posts, cursor):
#     for post in posts:
#        cursor.execute('INSERT OR IGNORE INTO Posts (id, message, created_time, likes_count) VALUES (?, ?, ?, ?)',
#                    (post['id'], post['message'], post['time'], post['likes']))
#        cursor.execute('UPDATE Posts SET message=?, likes_count=? WHERE id=?', (post['message'], post['likes'], post['id']))
#        for comment in post['comments']:
#            cursor.execute('INSERT OR IGNORE INTO Comments (id, message_id, comment, created_time) VALUES (?, ?, ?, ?)',
#                        (comment['id'], post['id'], comment['comment'], comment['time']))
#        cursor.execute('UPDATE Comments SET comment=? WHERE id=?', (comment['comment'], comment['id']))


def main():
    name = input('Введите название учетную запись facebook(по умолчанию будет выбрана страница телеканала Дождь - tvrain): ')
    if len(name) < 1: name = 'tvrain'
    a = input('Введите кол-во постов для парсинга (по умолчанию - 100): ')
    if len(a) < 1: post_count=100
    else:
        try: post_count = int(a)
        except: post_count=100

    conn = sqlite3.connect(name + '.sqlite')
    cur = conn.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS Posts (id TEXT PRIMARY KEY, message TEXT, created_time TEXT, likes_count INTEGER);
    CREATE TABLE IF NOT EXISTS Comments (id TEXT PRIMARY KEY, message_id INTEGER, comment TEXT, created_time TEXT);
    ''')
    conn.commit()
    posts = list()
    get_posts(get_url_posts(name), posts, cur, conn, post_count)
#    insert_into_db(posts, cur)

    print (posts)


if __name__ == '__main__':
    main()


