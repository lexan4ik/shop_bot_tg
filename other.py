from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton
from functions_db import BotDB
import telebot
import sqlite3 as sl
import json

BotDB = BotDB('User_DB.db')


#Для обработки регистрации пользователей
register = {}

#Для обработки добавление товаров
product_add = {}

#Для редактирования сообщений
message_edit = {}

#Для редактирования сообщений в Админ чате
message_edit_chat_admin = {}

#Для изменения администраторов
admin_edit = {}

#Для добавления администраторов
list_adm = {}

#Для редактирования сообщения продавцов
message_edit_seller = {}


con = sl.connect('User_DB.db', check_same_thread=False)


#Создание таблив базы данных
with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS USER (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tg_id INT,
        first_name CHARACTER,
        last_name CHARACTER,
        address VARCHAR,
        phone INT,
        UNIQUE(tg_id),
        UNIQUE(phone)
        );""")
    con.execute("""CREATE TABLE IF NOT EXISTS PRODUCTS (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tg_id INT,
        prod_id INT NOT NULL DEFAULT 10000,
        name_product VARCHAR,
        category VARCHAR,
        price_product REAL,
        description VARCHAR,
        photo TEXT,
        UNIQUE(prod_id)
        );""")
    con.execute("""CREATE TABLE IF NOT EXISTS CART (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tg_id INT,
        prod_id INT,
        count INT NOT NULL DEFAULT 1,
        UNIQUE(prod_id)
        );""")
    con.execute("""CREATE TABLE IF NOT EXISTS USER_ORDER (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        id_order INT NOT NULL DEFAULT '100000',
        tg_id INT,
        prod_id INT,
        count INT,
        status NCHAR DEFAULT 'Ожидает обработки',
        delivery VARCHAR
        );""")
    con.execute("""CREATE TABLE IF NOT EXISTS ADMIN (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        tg_id INT,
        name_admin NCHAR,
        right NCHAR,
        UNIQUE(tg_id)
        );""")

#Загрузка данных из json файла
def load_setting(module):
    try:
        with open("setting.json", encoding='utf-8') as f:
            settings = json.loads(f.read())

        return settings[module]
    except:
        print(f'Файл setting не найден или вы ввели не правильно данные!')
        pass

def add_admin(tg_id,name,right):
    print(f'Файл setting инициализирован')
    if BotDB.admin_exists(tg_id) is True:
        print('Администрато уже существует, пропускаем')
    else:
        BotDB.add_admin(tg_id,name,right)
        print(f'Пользователь {name} с ID: {tg_id} Добавлен как {right}')


add_admin(load_setting("ADMIN_TG_ID"), load_setting("ADMIN_NAME"), load_setting("ADMIN_RIGHT"))

TOKEN = load_setting('TOKEN')

bot = telebot.TeleBot(TOKEN)


#Доступные категории для добавления товаров продавцами
category = load_setting('CATEGORY')
print(load_setting('CATEGORY'))
#Админ чат для отправки заказов или важных сообщений
admin_chat_id = load_setting('ADMINCHAT')



#Клавиатуры для пользования из бота
#Генерация меню
product_ = KeyboardButton('Товары')
cart_ = KeyboardButton('Моя корзина')
order_ = KeyboardButton('Мои заказы')
help_ = KeyboardButton('Помощь')
my_info_ = KeyboardButton('Мои данные')

menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu.row(product_,cart_)
menu.row(order_,my_info_)
menu.add(help_)

#Клавиатура для подтверждения создания товара
keyb_confirm_product = InlineKeyboardMarkup()
keyb_confirm_product.add(InlineKeyboardButton('Да',callback_data='yes_add0'),InlineKeyboardButton('Нет',callback_data='nop_add0'))

#Клавиатура для подтверждения оформления заказа
confirm_order = InlineKeyboardMarkup()
confirm_order.add(InlineKeyboardButton('Заказать!',callback_data='addorder'),InlineKeyboardButton('Отмена!',callback_data='cancel'))

#Клавиатура для выбора доставки или самовывоза
delivery_method = InlineKeyboardMarkup()
delivery_method.add(InlineKeyboardButton('Почта',callback_data='mailmetd'),InlineKeyboardButton('Самовывоз',callback_data='pickmetd'))

#Клавиатура для подтверждения регистрации
keyb_register = InlineKeyboardMarkup()
keyb_register.add(InlineKeyboardButton('Зарегестрироваться',callback_data='yesregister'),InlineKeyboardButton('Нет',callback_data='noregister'))

#Клавиатуры для пользования из админ чата
#Выдача меню
admin_order_ = KeyboardButton('Показать заказы')


admin_menu = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin_menu.row(admin_order_)

#Меню для супер Администратора
super_admin_keyb = InlineKeyboardMarkup()

super_admin_keyb.add(InlineKeyboardButton('Показать всех админов', callback_data='showadmn'))
super_admin_keyb.add(InlineKeyboardButton('Показать продавцов', callback_data='shwseler'))
super_admin_keyb.add(InlineKeyboardButton('Добавить админа или продавца', callback_data='addadmin'))
super_admin_keyb.add(InlineKeyboardButton('Добавить товар', callback_data='yes_add0'))
super_admin_keyb.add(InlineKeyboardButton('Мои товары', callback_data='myprodct'))

#Изменение прав для администратора
keyb_seller = InlineKeyboardMarkup()

keyb_seller.add(InlineKeyboardButton('Добавить товар', callback_data='yes_add0'))
keyb_seller.add(InlineKeyboardButton('Мои товары', callback_data='myprodct'))

