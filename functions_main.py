from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,InputMediaPhoto
from other import message_edit,bot,list_adm, message_edit_seller
from functions_db import BotDB

BotDB = BotDB('User_DB.db')

#Генерация категорий при добавления товара
def category_add(category):
    keyb_category_for_product = InlineKeyboardMarkup()
    for i in category:
        index = category.index(i)
        keyb_category_for_product.add(InlineKeyboardButton(i,callback_data=f'category{index}'))
    return keyb_category_for_product

#Генерация карточки и обработка кнопок перелистования и кол-ва товара в корзине
def card(user_id,data, num, flag=''):
    result = BotDB.category_search(data)
    num = int(num)
    try:
        for i in result[num]:
            text = f"{result[num][1]} ({result[num][0]})\n\n{result[num][3]} byn\n\n{result[num][4]}\n\n"
            photo = result[num][5]
            cart_add = InlineKeyboardMarkup()

            if len(result)-1 == 0 and num == 0:
                pass
            elif num == 0:
                cart_add.add(InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'), InlineKeyboardButton('➡️', callback_data=f'keybord4{num + 1}'))
            elif num != 0 and num != len(result)-1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord3{num - 1}'), InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),InlineKeyboardButton('➡️', callback_data=f'keybord4{num + 1}'))
            elif num == len(result)-1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord3{num - 1}'), InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'))

        if flag == 'count_cart':
            count = BotDB.count_to_cart(user_id, result[num][0])
            cart_add.add(InlineKeyboardButton('⬇️', callback_data=f'delcount{result[num][0]}'),
                         InlineKeyboardButton(f'{count[0]}', callback_data='cartcount'),
                         InlineKeyboardButton('⬆️', callback_data=f'addcount{result[num][0]}'))
            cart_add.add(InlineKeyboardButton('Товар уже в корзине!',callback_data='prod_exists'))

        elif BotDB.prod_cart_exists(user_id,result[num][0]) is True:
            count = BotDB.count_to_cart(user_id, result[num][0])
            cart_add.add(InlineKeyboardButton('⬇️', callback_data=f'delcount{result[num][0]}'),
                         InlineKeyboardButton(f'{count[0]}', callback_data='cartcount'),
                         InlineKeyboardButton('⬆️', callback_data=f'addcount{result[num][0]}'))
            cart_add.add(InlineKeyboardButton('Товар уже в корзине!',callback_data='prod_exists'))

        elif flag == 'cart':
            full_price = BotDB.price_cart(user_id)
            for i in full_price:
                print(i)
            count = BotDB.count_to_cart(user_id, result[num][0])
            cart_add.add(InlineKeyboardButton('-', callback_data=f'delcount{result[num][0]}'),
                         InlineKeyboardButton(f'{count[0]}', callback_data='cartcount'),
                         InlineKeyboardButton('+', callback_data=f'addcount{result[num][0]}'))

        elif flag == 'delproduct':
            cart_add.add(InlineKeyboardButton('Удалить товар?',callback_data=f'delcart0{result[num][0]}'),InlineKeyboardButton('Отмена',callback_data='delcanc0'))

        else:
            cart_add.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'add_cart{result[num][0]}'))

        if 'product' not in message_edit[user_id]:
            mess_id = bot.send_photo(user_id, photo, caption=text, reply_markup=cart_add)
            message_edit[user_id]['product'] = mess_id.id
            message_edit[user_id]['num'] = num
        else:
            media = InputMediaPhoto(photo, caption=text)
            bot.edit_message_media(media=media, chat_id=user_id, message_id=message_edit[user_id]['product'],
                                   reply_markup=cart_add)
            message_edit[user_id]['num'] = num

    except IndexError:
        print('Обращение к старому сообщению с товарами')

#Выдача корзины и обработка кнопок
def cart(user_id, num, flag=''):
    result = BotDB.product_search(user_id)
    print(result)
    num = int(num)
    if num == -1:
        num = 0
    try:
        for i in result[num]:
            text = f"{result[num][1]} ({result[num][0]})\n\n{result[num][3]} byn\n\n{result[num][4]}\n\n"
            photo = result[num][5]
            cart_add = InlineKeyboardMarkup(row_width=4)

            if len(result) - 1 == 0 and num == 0:
                pass
            elif num == 0:
                cart_add.add(InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'), InlineKeyboardButton('➡️', callback_data=f'keybord4{num + 1}'))
            elif num != 0 and num != len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord3{num - 1}'), InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord4{num + 1}'))
            elif num == len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord3{num - 1}'), InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'))


        count = BotDB.count_to_cart(user_id, result[num][0])
        cart_add.add(InlineKeyboardButton('✖️',callback_data=f'delcart1{result[num][0]}'),InlineKeyboardButton('⬇️', callback_data=f'delcount{result[num][0]}'),
                     InlineKeyboardButton(f'{count[0]}', callback_data='cartcount'),
                     InlineKeyboardButton('⬆️', callback_data=f'addcount{result[num][0]}'))

        if flag == 'delproduct':
            cart_add.add(InlineKeyboardButton('☑Удалить?', callback_data=f'delcart0{result[num][0]}'), InlineKeyboardButton('Отмена', callback_data='delcanc0'))

        cart_add.add(InlineKeyboardButton(f'Сумма товара: {count[0]} * {result[num][3]} = {float("{:.2f}".format(count[0]*result[num][3]))} byn', callback_data='cartcount'))
        count_price = BotDB.price_cart(user_id)
        full_price = 0
        for i in count_price:
            full_price += i[0]
        cart_add.add(InlineKeyboardButton(f'Стоимость корзины: {float("{:.2f}".format(full_price))} byn',callback_data='fullprice'))


        cart_add.add(InlineKeyboardButton('Оформить заказ?',callback_data='confirm0'),InlineKeyboardButton('✅',callback_data='confirm0'))

        if 'product_cart' not in message_edit[user_id]:
            mess_id = bot.send_photo(user_id, photo, caption=text, reply_markup=cart_add)
            message_edit[user_id]['product_cart'] = mess_id.id
            message_edit[user_id]['num_cart'] = num

        else:
            media = InputMediaPhoto(photo, caption=text)
            bot.edit_message_media(media=media, chat_id=user_id, message_id=message_edit[user_id]['product_cart'],
                                   reply_markup=cart_add)
            message_edit[user_id]['num_cart'] = num
    except IndexError:
        print('Обращение к старому сообщению с товарами')

#Поиск заказов и генерация клавиатуры с id_order и вызов функции order для выдачи карточки пользователю
def order_id(user_id):
    keyb_order_id = InlineKeyboardMarkup()
    orders = BotDB.search_order_id(user_id)
    orders = list(set(orders))
    for i in orders:
        keyb_order_id.add(InlineKeyboardButton(f'Заказ N{i[0]} : {i[1]}',callback_data=f'myorders{i[0]}'))
    return keyb_order_id


#Выдача заказов
def order(user_id,num,id_order):
    result = BotDB.order(user_id, id_order)
    print(result)
    num = int(num)
    if num == -1:
        num = 0
    try:
        for i in result:
            if result[num][8] in i:
                print(result[num][8])
            text = f"Заказ N{result[num][8]}\n\n{result[num][2]} ({result[num][1]})\n\nКоличество: {result[num][5]}\n\n{result[num][3]} byn\n\nСтатус: {result[num][6]}\n\n{result[num][7]}"
            photo = result[num][4]
            cart_add = InlineKeyboardMarkup(row_width=4)

            if len(result) - 1 == 0 and num == 0:
                pass
            elif num == 0:
                cart_add.add(InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord5{num + 1}'))
            elif num != 0 and num != len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord6{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord5{num + 1}'))
            elif num == len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord6{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'))

        cart_add.add(InlineKeyboardButton(
            f'Сумма товара: {result[num][5]} * {result[num][3]} = {float("{:.2f}".format(result[num][5] * result[num][3]))} byn',
            callback_data='cartcount'))

        full_price = 0
        for i in result:
            full_price += float(i[3])*float(i[5])
        cart_add.add(InlineKeyboardButton(f'Стоимость заказа: {float("{:.2f}".format(full_price))} byn',
                                          callback_data='fullprice'))
        if 'order_list' not in message_edit[user_id]:
            mess_id = bot.send_photo(user_id, photo, caption=text, reply_markup=cart_add)
            message_edit[user_id]['order_list'] = mess_id.id
            message_edit[user_id]['num_order'] = num
            message_edit[user_id]['id_order'] = id_order
        else:
            media = InputMediaPhoto(photo, caption=text)
            bot.edit_message_media(media=media, chat_id=user_id, message_id=message_edit[user_id]['order_list'],
                                   reply_markup=cart_add)
            message_edit[user_id]['num_order'] = num
    except IndexError:
        print('Обращение к старому сообщению с товарами')

#Генерация кнопок с категориями
def key_gen_category(list_, num, fix_poz=7, flag="x", flag2="f"):
    il = InlineKeyboardMarkup()
    if ((num + 1) * fix_poz) < len(list_):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(list_)

    for x in range(num * fix_poz, end_):
        il.add(InlineKeyboardButton(list_[x], callback_data=flag2 + str(list_[x])))
    if num == 0 and len(list_) < fix_poz:
        il.add(InlineKeyboardButton("В меню", callback_data="m"))
    elif num == 0:
        il.add(InlineKeyboardButton("В меню", callback_data="m"),InlineKeyboardButton("Дальше", callback_data=flag + str(num + 1)))
    elif num != 0 and end_ == len(list_):
        il.add(InlineKeyboardButton("Назад", callback_data=flag + str(num - 1)),InlineKeyboardButton("В меню", callback_data="m"))
    else:
        il.add(InlineKeyboardButton("Назад", callback_data=flag + str(num - 1)),
               InlineKeyboardButton("В меню", callback_data="m"),
               InlineKeyboardButton("Дальше", callback_data=flag + str(num + 1)))
    return il


def admin_list():
    keyb_admin_list = InlineKeyboardMarkup()
    admin = BotDB.search_admin()
    for i in admin:
        keyb_admin_list.add(InlineKeyboardButton(f'{i[1]} : {i[2]}', callback_data=f'adminstr{i[0]}'))
    return keyb_admin_list

def seller_list(chat_id):
    keyb_seller_list = InlineKeyboardMarkup()
    seller = BotDB.search_seller()
    if seller != []:
        for i in seller:
            keyb_seller_list.add(InlineKeyboardButton(f'{i[1]} : {i[2]}', callback_data=f'adminstr{i[0]}'))
        bot.send_message(chat_id, 'Все продавцы:', reply_markup=keyb_seller_list)
    else:
        bot.send_message(chat_id,'Продавцов не найдено')

def edit_admin(user_id):
    edit_admin_keyb = InlineKeyboardMarkup()
    edit_admin_keyb.add(InlineKeyboardButton('Изменить имя', callback_data=f'chngname{user_id}'),
                        InlineKeyboardButton('Изменить права', callback_data=f'chngrght{user_id}'))
    edit_admin_keyb.add(InlineKeyboardButton('Удалить админа?', callback_data=f'deladmin{user_id}'))
    return edit_admin_keyb

def new_admin(message):
    admin_keyb = InlineKeyboardMarkup()
    forward_id = message.forward_from

    list_adm[message.chat.id] = {}
    try:
        if forward_id.username is not None:
            list_adm[message.chat.id]['id'] = forward_id.id
            list_adm[message.chat.id]['username'] = forward_id.username
        elif forward_id.first_name is not None and forward_id.username is None:
            list_adm[message.chat.id]['id'] = forward_id.id
            list_adm[message.chat.id]['first_name'] = forward_id.first_name
        else:
            list_adm[message.chat.id]['id'] = forward_id.id
        admin_keyb.add(InlineKeyboardButton('Администратор', callback_data=f'ad_admin{list}'),
                       InlineKeyboardButton('Супер Админ', callback_data=f'addsuper{list}'),
                       InlineKeyboardButton('Продавец', callback_data=f'ad_seler{list}'))
        print(list_adm)
        return admin_keyb
    except:
        del list_adm[message.chat.id]
        bot.send_message(message.chat.id, 'Добавление отменено')


def seller_product(user_id,num):
    result = BotDB.product_search_id(user_id)
    print(result)
    num = int(num)
    if num == -1:
        num = 0
    try:
        for i in result[num]:
            text = f"{result[num][1]} ({result[num][0]})\n\n{result[num][3]} byn\n\n{result[num][4]}\n\n"
            photo = result[num][5]
            cart_add = InlineKeyboardMarkup(row_width=4)

            if len(result) - 1 == 0 and num == 0:
                pass
            elif num == 0:
                cart_add.add(InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord8{num + 1}'))
            elif num != 0 and num != len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord7{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord8{num + 1}'))
            elif num == len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord7{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'))

        if 'product_cart' not in message_edit_seller[user_id]:
            mess_id = bot.send_photo(user_id, photo, caption=text, reply_markup=cart_add)
            message_edit_seller[user_id]['product_cart'] = mess_id.id
            message_edit_seller[user_id]['num_cart'] = num

        else:
            media = InputMediaPhoto(photo, caption=text)
            bot.edit_message_media(media=media, chat_id=user_id, message_id=message_edit_seller[user_id]['product_cart'],
                                   reply_markup=cart_add)
            message_edit_seller[user_id]['num_cart'] = num
    except IndexError:
        print('Обращение к старому сообщению с товарами')