# [WORKID: TGE UPDATE] Blum-Farm
4.4.25 - ну че чюваки там новый TGE, нужно от 100k BP: добро пожаловать, снова
![1](https://github.com/club100-blum/Blum/assets/175149065/4a20c325-ed6c-47bd-941c-ec92819bbcc3)


Blum-Farm - программное обеспечение для автоматизированного фарма в телеграме, с простейшей настройкой. Позволяет как запустить фарм для основного аккаунта, так и создать целый комбайн.
Сделано для [TheClub100](https://t.me/the_club_100)

[Инструкция по установке в Telegraph](https://telegra.ph/Blum-Auto-Farm-dlya-The-Club-100-07-08)

### Функции
1) **24/7 фарм** ежедневых бонусов, задач, прохождение игр с прогрешностью в баллах для обхода античита с существующих аккаунтов.
2) **Первый запуск** блума с большого количества ваших аккаунтов с вашей рефералкой. Если количество использовании у реф-ссылки закончится, использует следующую реферальную ссылку.
3) **Создание сессий Pyrogram**. Вы можете ввести номер телефона и полученный код для сохранении аккаунта в формате `pyrogram .session`.

### Режимы работы
- **Ленивый режим** (`lazy`) - софт работает из коробки без настройки и прокси. Запускаете телеграм, после этого запускаете программу в режиме `lazy`. Программа сама найдет ваши телеграм аккаунты в запущенном процессе `Telegram.exe` и с них начнет фармить блум.
    - данный режим включен по умолчанию
    - используется API_ID, API_HASH от `telegram.exe`, не нужно ничего настраивать
    - безопасность для ваших сессии гарантируется - айпи и данные устроиства у софта будут совпадать с телеграмом запущенном на вашем компьютере 
- **Аккаунты pyrogram** (`pyrogram`) - программа возьмет сессии с папки sessions. 
    - cессии могут быть добавлены с помощи 3-ей функции софта 
    - используется API_ID, API_HASH настроенный в `config.py`
- **Аккаунты telethon** (`telethon`) - программа возьмет сессии с папки sessions в формате .session.
    - используется API_ID, API_HASH настроенный в `config.py`
- **Аккаунты telethon+json** (`telethon+json`) - программа возьмет сессии с папки sessions в формате `.session` и `.json`.
    - совместима с авторегистратором аккаунтов **TG Pixel** и другими софтами
    - используется API_ID, API_HASH, SDK и тд. из файла `.json`. Конфиги в `config.py` игнорируются.
    - поддерживает мобильные прокси которые автоматический подбираются под номер телефона по стране
    - используется для больших ферм



### Установка


1. **Для Windows**
 - Установите Python последней версии поставив галочку в пукнте .PATH https://www.python.org/downloads/, обязательно поставьте галочку на .PATH

 - Скачайте релиз гитхаба архивом и распакуйте

1. **Для Unix-систем**

    ```bash
    git clone https://github.com/folqc-dev/Blum
    cd Blum
    ```

   
    

2. **Запустите скрипт:**
    Запустите CMD в директории с файлами и вручную пропишите

    - pip install -r requirements.txt
    - py main.py 
    - или
    - python main.py
    
    Или выполните команду `sh run.sh` если у вас Unix-система.

### Конфигурация

Конфигурации в файле `data/config.py`. Откройте его в блокноте или в любом удобном редакторе кода, чтобы изменить: режим работы, задержку между фармом, разброс между очками и количество одновременно работающих аккаунтов.

### Прокси (необязательно)
#### Файл `data/proxy.txt`
- Добавьте ваши прокси в `data/proxy.txt` в формате `login:password@host:port` и укажите `PROXY = True` в конфигах. Можете добавить как обычные прокси так и мобильные, rotating.
#### Сервис [Dataimpulse](https://dataimpulse.com) 
- Работает только в режиме `telethon+json`
- Мобильный/Резидентский прокси автоматический подбирается по стране номера телефона каждого аккаунта Telegram
- Укажите `DATAIMPULSE = TRUE` и так же укажите ваш логин и пароль от плана прокси. 


### Использование

1. **Запустите скрипт:**
    Запустите CMD в папке со скриптом. 
    ``` py main.py```, или ```python main.py```
    
    или 
    
    ```run.sh```, если у вас UNIX-система

2. **Выберите действие:**
    - `1` Запуск основного фарма 
    - `2` Первый старт блума через рефералку с ваших аккаунтов. (используйте если аккаунты пустые и с них не запускали ранее блум)
    - `3` Создание сессии pyrogram

### Контакт

Для поддержки или вопросов свяжитесь со мной в Telegram: [@folqc](https://t.me/folqc)
