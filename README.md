### Мини социальная сеть
Описание:
	Простая социальной сеть с возможностью создания учетных записей и публикации.  Система подписок и отметок "Нравится".

### Технологии
- Django==2.2.16
- django-debug-toolbar==2.2
- Faker==12.0.1
- Pillow==8.3.1
- pip==23.0.1
- pytest==6.2.4
- requests==2.26.0

### Настройка проекта (Linux)
Установить Python 3.9 (Ubuntu):

Запустите Терминал (если Вы работаете в графической среде Ubuntu), нажав на комбинацию клавиш Ctrl Alt T.

Обновляем список источников ПО, включаем поддержку источников независимых поставщиков ПО, выполнив команду:
```
sudo apt update && sudo apt install software-properties-common
```
Добавьте репозиторий, в котором находится Python 3.9:
```
sudo add-apt-repository ppa:deadsnakes/ppa
```
Выполните команду установки Python 3.9:
```
sudo apt install python3.9
```
Проверьте установленную версию Python:
```
python3.9 --version
```
- Устоновить git:
```
sudo apt install git
```
- Убедиться в правильности установки Git можно:
```
git --version
```
- Установить pip3:
```
sudo apt -y install python3-pip
```
- Проверка правильности устоновки pip:
```
pip3 --version
```
- Клонировать репозиторий

```
git clone https://github.com/vitalikShcerbakov/mini_social_network.git
```

- Перейти в каталог с проектом:

```
cd mini_social_network
```

- Cозать вертуальное окружение venv:

```
python3.9 -m venv venv
```

- Активировать виртуальное окружение:

```
source venv/bin/activate
```

-Установить зависимости:

```
pip install -r requirements.txt
```

### Запуск проекта в dev-режиме

- В папке с файлом manage.py выполните команды:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

```