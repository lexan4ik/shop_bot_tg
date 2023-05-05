import telebot.apihelper
from telebot.types import KeyboardButton
from functions_admin_chat import *

@bot.message_handler(content_types=['text'],chat_types=['supergroup'])
def start_admin(message):
    chat_id = admin_chat_id
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    admin_status = BotDB.admin_status(user_id)
    print(admin_status)

    if admin_status is None:
        if username is not None:
            bot.send_message(admin_chat_id, f'Пользователь {username} как вы сюда попали?\n\nВаш ID: {user_id}')
        elif first_name is not None:
            bot.send_message(admin_chat_id, f'Пользователь {first_name}\n\nВаш ID: {user_id}')
        else:
            bot.send_message(admin_chat_id, f'Пользователь ??? как вы сюда попали\n\nВаш ID: {user_id}')
    if BotDB.admin_exists(user_id) is True:
        if admin_status[0] != 'Продавец':
            if message.text == '/start@Traiiingg_bot' or message.text == '/start' and message.chat.id == admin_chat_id:

                message_edit_chat_admin[chat_id] = {}
                if username is not None:
                    bot.send_message(admin_chat_id, f'Приветствую в админ чате {username}\n\nВаш ID: {user_id}', reply_markup=admin_menu)
                elif first_name is not None:
                    bot.send_message(admin_chat_id, f'Приветствую в админ чате {first_name}\n\nВаш ID: {user_id}', reply_markup=admin_menu)
                else:
                    bot.send_message(admin_chat_id, f'Приветсвую в админ чате Администратор\n\nВаш ID: {user_id}', reply_markup=admin_menu)
            elif message.text == 'Показать заказы':
                message_edit_chat_admin[chat_id] = {}
                mess = bot.send_message(admin_chat_id, 'Все активные заказы', reply_markup=order_admin_keyb())
                message_edit_chat_admin[chat_id]['del_order_list'] = mess.id

        if chat_id in message_edit_chat_admin and 'edit_stat' in message_edit_chat_admin[chat_id] and message_edit_chat_admin[chat_id]['edit_stat'] is True:
            print(message.text)
            BotDB.change_status_order(message_edit_chat_admin[chat_id]['id_order'], message.text)
            message_edit_chat_admin[chat_id]['edit_stat'] = False
            order_admin_list(message_edit_chat_admin[chat_id]['id_order'], 0)

@bot.callback_query_handler(func=lambda call: call.message.chat.type == 'supergroup')
def answer_admin(call):
    bot.answer_callback_query(callback_query_id=call.id,)
    chat_id = admin_chat_id
    user_id = call.message.from_user.id
    flag = call.data[0:9]
    data = call.data[9:]

    print('admin flag', flag)
    print('admin data', data)
    if flag == 'addright0':
        BotDB.add_admin(data,'NoName','Продавец')
    if flag == 'adm_order':
        bot.delete_message(chat_id=chat_id,message_id=message_edit_chat_admin[chat_id]['del_order_list'])
        order_admin_list(data,0)

    if flag == 'keybord_5':
        order_admin_list(message_edit_chat_admin[chat_id]['id_order'], int(data))

    if flag == 'keybord_6':
        order_admin_list(message_edit_chat_admin[chat_id]['id_order'], int(data))

    if flag == 'retrn_ord':
        bot.delete_message(chat_id=chat_id,message_id=message_edit_chat_admin[chat_id]['order_mess_id'])
        mess = bot.send_message(chat_id,'Все активные заказы',reply_markup=order_admin_keyb())
        message_edit_chat_admin[chat_id]['del_order_list'] = mess.id

    if flag == 'chng_stat':
        bot.send_message(chat_id,'Введите статус для данного заказа на который хотите сменить или введите "отмена" для отмены изменения')
        message_edit_chat_admin[chat_id]['edit_stat'] = True
