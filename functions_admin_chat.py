from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton,InputMediaPhoto
from other import bot, admin_chat_id, message_edit_chat_admin,admin_menu,super_admin_keyb
from functions_db import BotDB

BotDB = BotDB('User_DB.db')


def order_admin_keyb():
    keyb_order_all = InlineKeyboardMarkup()
    orders = BotDB.search_all_order()
    orders = list(set(orders))
    for i in orders:
        print(i)
        keyb_order_all.add(InlineKeyboardButton(f'Заказ N{i[1]} : {i[2]}',callback_data=f'adm_order{i[1]}'))
    return keyb_order_all

#Выдача заказов
def order_admin_list(id_order,num):
    chat_id = admin_chat_id
    result = BotDB.search_order_id_order(id_order)
    num = int(num)
    print(result)
    if num == -1:
        num = 0
    try:
        for i in result:
            user_info = BotDB.info_user(result[num][9])
            cart_add = InlineKeyboardMarkup(row_width=4)
            text_info = f'Имя: {user_info[0]}\n\nФамилия: {user_info[1]}\n\nАдрес доставки: {user_info[2]}\n\nНомер телефона: {user_info[3]}\n\n'
            text = f"Заказ N{result[num][8]}  от {result[num][9]}\n\n{result[num][2]} ({result[num][1]})\n\nКоличество: {result[num][5]}\n\n{result[num][3]} byn\n\nСтатус: {result[num][6]}\n\n{result[num][7]}"
            photo = result[num][4]

            if len(result) - 1 == 0 and num == 0:
                pass
            elif num == 0:
                cart_add.add(InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord_5{num + 1}'))
            elif num != 0 and num != len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord_6{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'),
                             InlineKeyboardButton('➡️', callback_data=f'keybord_5{num + 1}'))
            elif num == len(result) - 1:
                cart_add.add(InlineKeyboardButton('⬅️', callback_data=f'keybord_6{num - 1}'),
                             InlineKeyboardButton(f'{num + 1} из {len(result)}', callback_data='cc'))

        cart_add.add(InlineKeyboardButton('Изменить статус заказа', callback_data=f'chng_stat{result[num][8]}'))

        cart_add.add(InlineKeyboardButton(
            f'Сумма товара: {result[num][5]} * {result[num][3]} = {float("{:.2f}".format(result[num][5] * result[num][3]))} byn',
            callback_data='cartcount'))

        full_price = 0
        for i in result:
            full_price += float(i[3])*float(i[5])
        cart_add.add(InlineKeyboardButton(f'Стоимость заказа: {float("{:.2f}".format(full_price))} byn',
                                          callback_data='fullprice'))

        cart_add.add(InlineKeyboardButton('Вернуться к списку заказов', callback_data='retrn_ord'))

        if 'order_list' not in message_edit_chat_admin[chat_id]:
            mess_id = bot.send_photo(admin_chat_id, photo, caption=text, reply_markup=cart_add)
            message_edit_chat_admin[chat_id]['order_mess_id'] = mess_id.id
            message_edit_chat_admin[chat_id]['num_list_order'] = num
            message_edit_chat_admin[chat_id]['id_order'] = id_order
        else:
            media = InputMediaPhoto(photo, caption=text)
            bot.edit_message_media(media=media, chat_id=admin_chat_id, message_id=message_edit_chat_admin[chat_id]['order_mess_id'],
                                   reply_markup=cart_add)
            message_edit_chat_admin[chat_id]['num_list_order'] = num
            message_edit_chat_admin[chat_id]['id_order'] = id_order
    except IndexError:
        print('Обращение к старому сообщению с товарами')
