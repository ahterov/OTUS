import scrap
import visualization

if __name__ == '__main__':
    while True:
        print('1 - Получить посты c facebook и положить из БД')
        print('2 - Визуализировать данные по постам из БД')
        print('0 - Выход')
        a = input('Выберите действие: ')
        if a == '0': break
        else:
            if a == '1': scrap.main()
            else: visualization.main()