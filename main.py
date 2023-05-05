import telebot.apihelper
from other import register,menu,product_add,category,keyb_confirm_product,\
    confirm_order,delivery_method,admin_chat_id,keyb_register, super_admin_keyb, admin_edit, list_adm
from admin_chat import start_admin,answer_admin
from functions_main import *

@bot.message_handler(content_types=['photo'])
def photo(message):
    user_id = message.chat.id
    if user_id in product_add and product_add[user_id]['status'] == 'photo':
        product_add[user_id]['photo'] = message.photo[-1].file_id
        product_add[user_id]['status'] = 'complete'
        list_product = []
        for a, b in product_add[user_id].items():
            if a != 'status':
                list_product.append(b)
        BotDB.add_product_db(list_product)
        bot.send_message(user_id, 'Товар успешно добавлен!')

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    print(message)
    print(user_id)
    if message.text == '/start':
        # Проверка юзера в бд и Регистрация пользователя
        if BotDB.user_exists(user_id) is False:
            bot.send_message(user_id,'Извините, вы не можете пользоваться ботом!')
            register[user_id] = {'status':'first_name'}
            register[user_id]['tg_id'] = user_id
            bot.send_message(user_id, 'Для использования бота пройдите пожалуйста регистрацию!', reply_markup=keyb_register)
        else:
            bot.send_message(user_id,'Добро пожаловать в наш магазин!', reply_markup=menu)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.chat.id
    admin_status = BotDB.admin_status(user_id)
    if message.text == '/admin' and admin_status[0] == 'Супер администратор':
        admin_edit[user_id] = {}
        message_edit_seller[user_id] = {}
        bot.send_message(user_id, 'Привествую Администатор', reply_markup=super_admin_keyb)

@bot.message_handler(commands=['seller'])
def seller(message):
    user_id = message.chat.id
    admin_status = BotDB.admin_status(user_id)
    keyb_seller = InlineKeyboardMarkup()

    keyb_seller.add(InlineKeyboardButton('Добавить товар', callback_data=f'yes_add0{user_id}'))
    keyb_seller.add(InlineKeyboardButton('Мои товары', callback_data=f'myprodct{user_id}'))

    if message.text == '/seller' and admin_status[0] == 'Продавец' or admin_status[0] == 'Супер администратор':
        message_edit_seller[user_id] = {}
        bot.send_message(user_id,'Добро пожаловать продавец', reply_markup=keyb_seller)


@bot.message_handler(content_types=['text'])
def spuff_message(message):
    user_id = message.chat.id
    text = message.text
    print(message)

    #Проверка регистрации пользователя в бд
    if BotDB.user_exists(user_id) is True:
    #Выдача меню если пользователь зарегистрирован
        if text.lower() == 'товары':
            bot.delete_message(user_id, message.id)
            if user_id not in message_edit:
                bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))
            elif user_id in message_edit:
                if 'product_cart' in message_edit[user_id]:
                    try:
                        bot.delete_message(user_id,message_edit[user_id]['product_cart'])
                        bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))
                    except:
                        bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))

                elif 'product' in message_edit[user_id]:
                    try:
                        bot.delete_message(user_id,message_edit[user_id]['product'])
                        bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))
                    except:
                        bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))
                else:
                    bot.send_message(user_id, 'Выберите категорию товара:',reply_markup=key_gen_category(BotDB.category(), 0, fix_poz=7, flag="keybord1",flag2="keybord2"))

        elif text.lower() == 'моя корзина':
            bot.delete_message(user_id,message.id)
            if BotDB.user_cart_exists(user_id) is False:
                bot.send_message(user_id, 'В вашей корзине пусто!')
            elif user_id in message_edit:
                if 'product' in message_edit[user_id]:
                    try:
                        bot.delete_message(user_id, message_edit[user_id]['product'])
                        message_edit[user_id] = {}
                        cart(user_id, 0)
                    except:
                        message_edit[user_id] = {}
                        cart(user_id, 0)

            elif user_id in message_edit:
                if 'product_cart' in message_edit[user_id]:
                    try:
                        bot.delete_message(user_id, message_edit[user_id]['product_cart'])
                        message_edit[user_id] = {}
                        cart(user_id, 0)
                    except:
                        message_edit[user_id] = {}
                        cart(user_id, 0)
            else:
                message_edit[user_id] = {}
                cart(user_id, 0)

        elif text.lower() == 'мои заказы':
            bot.delete_message(user_id,message.id)
            if BotDB.order_exists(user_id) is False:
                bot.send_message(user_id, 'У вас нету активных заказов')
            else:
                message_edit[user_id] = {}
                mess = bot.send_message(user_id,'Ваши заказы активные заказы:',reply_markup=order_id(user_id))
                message_edit[user_id]['order_mess'] = mess.id
                print('Заказы')

        elif text.lower() == 'помощь':
            bot.delete_message(user_id,message.id)
            help_keyb = InlineKeyboardMarkup()
            help_keyb.add(InlineKeyboardButton('Запросить права на продажу!', callback_data=f'getseler{user_id}'))
            bot.send_message(user_id,'Чем помочь?', reply_markup=help_keyb)

        elif text.lower() == 'мои данные':
            bot.delete_message(user_id,message.id)
            info = BotDB.info_user(user_id)
            info_text = f'Ваше имя: {info[0]}\n\nВаша фамилия: {info[1]}\n\nВаш адрес доставки: {info[2]}\n\nВаш номер телефона: {info[3]}'
            bot.send_message(user_id, info_text)

            print(info)



#Добавление товара
        if user_id not in product_add:
            pass
        else:
            if product_add[user_id]['status'] == 'name':
                product_add[user_id]['name'] = text
                product_add[user_id]['status'] = 'category'
                bot.send_message(user_id,'Выберите одну из категорий.', reply_markup=category_add(category))

            elif product_add[user_id]['status'] == 'price':
                if text.isdigit and float(text) or int(text):
                    product_add[user_id]['price'] = text
                    product_add[user_id]['status'] = 'desc'
                    bot.send_message(user_id,'Введите описание товара.')
                else:
                    bot.send_message(user_id,'Введите цену в виде: 34, 34.5, 34.54 ')
            elif product_add[user_id]['status'] == 'desc':
                product_add[user_id]['description'] = text
                product_add[user_id]['status'] = 'photo'
                bot.send_message(user_id,'Отправте фото товара')

            elif product_add[user_id]['status'] == 'photo':
                if message.photo:
                    pass
                else:
                    bot.send_message(user_id,'Отправте фотографию в сжатом формате')


#Регистрация пользователя
    if BotDB.user_exists(user_id) is False and message.chat.id != admin_chat_id:

        if register[user_id]['status'] == 'first_name':
            register[user_id]['first_name'] = text
            register[user_id]['status'] = 'last_name'
            bot.send_message(user_id,'Введите фамилию')

        elif register[user_id]['status'] == 'last_name':
            register[user_id]['last_name'] = text
            register[user_id]['status'] = 'address'
            bot.send_message(user_id,'Введите адрес для доставки\n\n В виде: Область,город,ул,дом')

        elif register[user_id]['status'] == 'address':
            register[user_id]['address'] = text
            register[user_id]['status'] = 'phone'
            bot.send_message(user_id,'Введите номер мобильного телефона\n\n В формате 375xxxxxxxx')

        elif register[user_id]['status'] == 'phone':
            if text.isdigit and len(text) == 12:
                register[user_id]['phone'] = text
                register[user_id]['status'] = 'complete'
                list_user = []
                for a,b in register[user_id].items():
                    if a != 'status':
                        list_user.append(b)
                BotDB.add_user(list_user)
                bot.send_message(user_id, 'Добро пожаловать в наш магазин!', reply_markup=menu)
            else:
                bot.send_message(user_id,'Проверьте номер телефона и введите еще раз')

    if BotDB.admin_status(user_id)[0] == 'Супер администратор':
        if user_id in admin_edit and 'name' in admin_edit[user_id] and admin_edit[user_id]['name'] is True:
            BotDB.change_name_admin(text, admin_edit[user_id]['name_id'])
            del admin_edit[user_id]

        elif user_id in admin_edit and 'right' in admin_edit[user_id] and admin_edit[user_id]['right'] is True:
            right_keyb = InlineKeyboardMarkup()
            if BotDB.admin_status(admin_edit[user_id]['name_id'])[0] == 'Администратор':
                right_keyb.add(InlineKeyboardButton('Супер админ', callback_data=''),InlineKeyboardButton('Продавец', callback_data=''))
            elif BotDB.admin_status(admin_edit[user_id]['name_id'])[0] == 'Супер администратор':
                right_keyb.add(InlineKeyboardButton('Администратор', callback_data=''),InlineKeyboardButton('Продавец', callback_data=''))

        elif text.lower() == 'добавить':
            bot.send_message(user_id, 'Хотите добавить товар?', reply_markup=keyb_confirm_product)
            product_add[user_id] = {'status': 'no'}
            product_add[user_id]['tg_id'] = user_id
            print('Добавление товара')

        elif user_id in admin_edit and 'addadmin' in admin_edit[user_id] and admin_edit[user_id]['addadmin'] is True:
            bot.send_message(user_id, 'Укажите уровень прав', reply_markup=new_admin(message))
            del admin_edit[user_id]
    if BotDB.admin_status(user_id)[0] == 'Продавец':
        if text.lower() == 'добавить':
            bot.send_message(user_id, 'Хотите добавить товар?', reply_markup=keyb_confirm_product)
            product_add[user_id] = {'status': 'no'}
            product_add[user_id]['tg_id'] = user_id
            print('Добавление товара')
@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    print(call.message)
    bot.answer_callback_query(callback_query_id=call.id,)
    id = call.message.chat.id
    flag = call.data[0:8]
    data = call.data[8:]
    print('user flag',flag)
    print('user data',data)

    #Запрос прав на продажу
    if flag == 'getseler':
        get_seller_keyb = InlineKeyboardMarkup()
        get_seller_keyb.add(InlineKeyboardButton('Выдать права!',callback_data=f'addright0{id}'), InlineKeyboardButton('Отказ!',callback_data='nonono'))
        try:
            bot.send_message(admin_chat_id, f'Запрос прав на продажу от пользователя {call.message.chat.username}', reply_markup=get_seller_keyb)
        except:
            bot.send_message(admin_chat_id, f'Запрос прав на продажу от пользователя {call.message.chat.id}', reply_markup=get_seller_keyb)

    #Возврат в меню 
    if flag == 'menu':
        bot.send_message(user_id,'Добро пожаловать в наш магазин!', reply_markup=menu)

    #Показать всех Администраторов
    if flag == 'showadmn':
        bot.send_message(id, 'Все администраторы:', reply_markup=admin_list())

    #Показать всех Продавцов
    if flag == 'shwseler':
        seller_list(id)

    #Добавить Администатора
    if flag == 'addadmin':
        admin_edit[id]['addadmin'] = True
        bot.send_message(id, 'Перешлите сообщение кого хотите добавить.')

    #Добавить Администратора в правах
    if flag == 'ad_admin':
        try:
            if 'username' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['username'], 'Администратор')
                bot.send_message(id, f'Пользователь {list_adm[id]["username"]}\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Администратор')
            elif 'first_name' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['first_name'], 'Администратор')
                bot.send_message(id, f'Пользователь {list_adm[id]["id"]}\n\nID: {list_adm[id]["first_name"]}\n\nДобавлен как Администратор')
            else:
                BotDB.add_admin(list_adm[id]['id'], 'NoName', 'Администратор')
                bot.send_message(id, f'Пользователь NoName\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Администратор')
        except:
            bot.send_message(id, f'Этот пользователь возможно есть в базе данных')

    #Добавить Супер адмиинстратора в правах
    if flag == 'addsuper':
        try:
            if 'username' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['username'], 'Супер администратор')
                bot.send_message(id, f'Пользователь {list_adm[id]["username"]}\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Супер администратор')
            elif 'first_name' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['first_name'], 'Администратор')
                bot.send_message(id, f'Пользователь {list_adm[id]["id"]}\n\nID: {list_adm[id]["first_name"]}\n\nДобавлен как Супер администратор')
            else:
                BotDB.add_admin(list_adm[id]['id'], 'NoName', 'Администратор')
                bot.send_message(id, f'Пользователь NoName\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Супер администратор')
        except:
            bot.send_message(id, f'Этот пользователь возможно есть в базе данных')

    #Добавить Продавца в правах
    if flag == 'ad_seler':
        try:
            if 'username' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['username'], 'Продавец')
                bot.send_message(id, f'Пользователь {list_adm[id]["username"]}\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Продавец')
            elif 'first_name' in list_adm[id]:
                BotDB.add_admin(list_adm[id]['id'], list_adm[id]['first_name'], 'Продавец')
                bot.send_message(id, f'Пользователь {list_adm[id]["id"]}\n\nID: {list_adm[id]["first_name"]}\n\nДобавлен как Продавец')
            else:
                BotDB.add_admin(list_adm[id]['id'], 'NoName', 'Администратор')
                bot.send_message(id, f'Пользователь NoName\n\nID: {list_adm[id]["id"]}\n\nДобавлен как Продавец')
        except:
            bot.send_message(id, f'Этот пользователь возможно есть в базе данных')

    # Выдача кнопок для изменения определеного админа
    if flag == 'adminstr':
        admin = BotDB.search_admin_for_id(data)
        admin = admin[0]
        bot.send_message(id,
                         f'Администратор: {admin[1]}\n\nID: {admin[0]}\n\nСтатус: {admin[2]}\n\nЧто хотите сделать?',
                         reply_markup=edit_admin(data))

    # Именить имя для Администатора
    if flag == 'chngname':
        admin_edit[id]['name'] = True
        admin_edit[id]['name_id'] = data
        bot.send_message(id,'Введите имя на которое хотите сменить.')

    # Изменить права для Администатора
    if flag == 'chngrght':
        change_admin_right = InlineKeyboardMarkup()
        change_admin_right.add(InlineKeyboardButton('Администратор',callback_data=f'updadmin{data}'),InlineKeyboardButton('Продавец',callback_data=f'updseler{data}'))
        change_admin_right.add(InlineKeyboardButton('Супер администратор!',callback_data=f'updSadmn{data}'))
        admin_edit[id]['name_id'] = data

    #Изменение прав на Администратора
    if flag == 'upadmin':
       BotDB.update_right_admin(data, 'Администратор')

    #Изменение прав на Супер администратора
    if flag == 'updseler':
        BotDB.update_right_admin(data, 'Супер администратор')

    #Изменение прав на Продавца
    if flag == 'updSadmn':
        BotDB.update_right_admin(data, 'Продавец')


    # Удалить Администатора
    if flag == 'deladmin':
        BotDB.delete_admin(data)
        bot.send_message(id, f'Администратор с ID: {data} удален.')

    #Подтверждение регистрации
    if call.data == 'yesregister':
        if register[id]['status'] == 'first_name':
            bot.send_message(id, 'Введите ваше Имя')

    #Отказ от регистрации
    if call.data == 'noregister':
        bot.send_message(id, 'Вы отказались от регистрации в магазине.')
        del register[id]

    #Выдача карточки заказов пользователю
    if flag == 'myorders':
        bot.delete_message(id,message_edit[id]['order_mess'])
        order(id,0,int(data))

    #Обработка кнопок перелистывания для заказов пользователя
    if flag == 'keybord5':
        order(id,int(data),message_edit[id]['id_order'])
    if flag == 'keybord6':
        order(id,int(data),message_edit[id]['id_order'])

    #Обработка самовывоза
    if flag == 'pickmetd':
        bot.send_message(id,'Функция в разработке!')

    #Обработка для заказа по почте
    if flag == 'mailmetd':
        price = BotDB.price_cart(id)
        full_price = 0
        for i in price:
            full_price += i[0]
        ss = BotDB.cart_to_order(id,'Доставка почтой')
        bot.send_message(id,f'Вы успешно оформили заказ с доставкой по почте!\n\nНомер вашего заказа: N{ss[1]}\n\nСумма вашего заказа: {float("{:.2f}".format(full_price))} byn\n\nВы можете отслеживать статус заказов в меню "Мои заказы"')
        bot.send_message(admin_chat_id, f'Новый заказ N{ss[1]}')

    #Оформление заказа
    if flag == 'confirm0':
        bot.delete_message(id,message_edit[id]['product_cart'])
        info = BotDB.info_user(id)
        info_text = f'Ваше имя: {info[0]}\n\nВаша фамилия: {info[1]}\n\nВаш адрес доставки: {info[2]}\n\nВаш номер телефона: {info[3]}\n\nПроверте правильность данных!\n\nВы можете изменить данные в меню "Мои данные"'
        bot.send_message(id,info_text,reply_markup=confirm_order)

    #Для подтверждения оформления заказа
    if flag == 'addorder':
        bot.send_message(id,'Выберите способ доставки', reply_markup=delivery_method)

    #Для отмены оформления заказа
    if flag == 'cancel':
        bot.send_message(id,'Вы отменили оформление заказа',reply_markup=menu)

    #Добавление товара или выдача кнопок для кол-ва товара
    if flag == 'add_cart':
        if BotDB.prod_cart_exists(id,data) is True:
            bot.send_message(id,'Этот товар уже у вас в корзине!')
            card(id,message_edit[id]['data'],message_edit[id]['num'],flag='count_cart')
        else:
            BotDB.add_to_cart(id,data)
            card(id,message_edit[id]['data'],message_edit[id]['num'],flag='count_cart')

    #Добавление кол-ва товара из карточки товара
    if flag == 'addcount':
        count = BotDB.count_to_cart(id,data)
        try:
            if count[0] >=10:
                bot.send_message(id,'Вы не можете добавить более 10шт в корзину, обратитесь к Администрации')
            else:
                BotDB.update_cart(id,data,count[0]+1)
                if 'data' not in message_edit[id] and 'product_cart' in message_edit[id]:
                    cart(id,message_edit[id]['num_cart'])
                elif 'data' in message_edit[id] and 'product_cart' not in message_edit[id]:
                    card(id,message_edit[id]['data'],message_edit[id]['num'],flag='count_cart')
        except TypeError:
            print('Оращение к старому или несуществующему сообщению')

    #Уменьшение кол-ва товара из карточки товара
    if flag == 'delcount':
        count = BotDB.count_to_cart(id,data)
        try:
            if count[0] == 1:
                if 'data' not in message_edit[id] and 'product_cart' in message_edit[id]:
                    cart(id, message_edit[id]['num_cart'], flag='delproduct')

                elif 'data' in message_edit[id] and 'product_cart' not in message_edit[id]:
                    card(id,message_edit[id]['data'],message_edit[id]['num'],flag='delproduct')
            else:
                BotDB.update_cart(id,data,count[0]-1)
                if 'data' not in message_edit[id] and 'product_cart' in message_edit[id]:
                    cart(id, message_edit[id]['num_cart'])

                elif 'data' in message_edit[id] and 'product_cart' not in message_edit[id]:
                    card(id, message_edit[id]['data'], message_edit[id]['num'], flag='count_cart')
        except TypeError:
            print('Оращение к старому или несуществующему сообщению')

    #Подтверждение удаление товара из корзины
    if flag == 'delcart1':
        if 'product_cart' in message_edit[id]:
            cart(id, message_edit[id]['num_cart'], flag='delproduct')

    # Удаление товара из корзины
    if flag == 'delcart0':
        BotDB.delete_cart(id, data)
        bot.send_message(id, 'Вы удалили товар из корзины.')
        if BotDB.user_cart_exists(id) is False:
            bot.delete_message(id,message_edit[id]['product_cart'])
            bot.send_message(id,'В вашей корзине пусто!')

        elif 'product' not in message_edit[id] and 'product_cart' in message_edit[id]:
            cart(id, message_edit[id]['num_cart']-1)

        elif 'data' in message_edit[id] and 'product_cart' not in message_edit[id]:
            card(id, message_edit[id]['data'], message_edit[id]['num'])

    # Отмена удаления товара из корзины
    if flag == 'delcanc0':
        bot.send_message(id, 'Вы отменили удаление товара.')
        if 'data' not in message_edit[id] and 'product_cart' in message_edit[id]:
            cart(id, message_edit[id]['num_cart'])
        elif 'data' in message_edit[id] and 'product_cart' not in message_edit[id]:
            card(id, message_edit[id]['data'], message_edit[id]['num'], flag='count_cart')

    #Обработка кнопки нажатия на категорию
    if flag == 'keybord2':
        bot.delete_message(id,call.message.id)
        message_edit[id] = {}
        message_edit[id]['data'] = data
        card(id,data,0)

    #Обработка кнопки пролистования товаров назад
    if flag == 'keybord3':
        try:
            if 'product' not in message_edit[id] and 'product_cart' in message_edit[id]:
                cart(id, data)
            else:
                card(id,message_edit[id]['data'], data)
        except:
            print('Оращение к старому или несуществующему сообщению')

    #Обработка кнопки пролистования товаров вперед
    if flag == 'keybord4':
        try:
            if 'product' not in message_edit[id] and 'product_cart' in message_edit[id]:
                cart(id, data)
            else:
                card(id, message_edit[id]['data'], data)
        except:
            print('Оращение к старому или несуществующему сообщению')

    #Показать всех товары пользователя
    if flag == 'myprodct':
        seller_product(id,0)

    if flag == 'keybord7':
        seller_product(id,data)

    if flag == 'keybord8':
        seller_product(id,data)

    #Подтверждение о добавлении товара
    if flag == 'yes_add0':
        bot.send_message(id,'Введите имя товара')
        product_add[id] = {'status':'name'}
        product_add[id]['tg_id'] = id

    #Отказ от добавления товара
    if flag == 'nop_add0':
        bot.send_message(id,'Вы отказались добавлять товар.')
        if id in product_add:
            del product_add[id]

    #Начало обработки добавление товара
    if flag == 'category':
        product_add[id]['category'] = category[int(data)]
        bot.send_message(id, 'Введите цену продукта.')
        product_add[id]['status'] = 'price'


if __name__ == "__main__":
    print("Bot started")
    bot.infinity_polling()
