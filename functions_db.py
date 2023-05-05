import sqlite3

class BotDB:

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    #Проверка пользователя на наличие в бд
    def user_exists(self, user_id):
        result = self.cursor.execute("SELECT id FROM user WHERE tg_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    #Добавление пользователя при регистрации
    def add_user(self,user):
        print(tuple(user))
        self.cursor.execute("INSERT INTO user (tg_id,first_name,last_name,address,phone) VALUES (?,?,?,?,?)", user)
        return self.conn.commit()

    #Проверка на наличие id и добавление продукта с новым id
    def add_product_db(self, data_product):
        try:
            res = self.cursor.execute("""SELECT MAX(prod_id) FROM products""")
            prod = res.fetchall()[0]
            data_product.insert(1, prod[0] + 1)
            self.cursor.execute("""INSERT INTO products (tg_id,prod_id,name_product,category,price_product,description,
                                        photo) VALUES (?,?,?,?,?,?,?)""", data_product)
        except:
            self.cursor.execute("""INSERT INTO products (tg_id,name_product,category,price_product,description,
                    photo) VALUES (?,?,?,?,?,?)""", data_product)
        return self.conn.commit()

    #Поиск товаров по категории для выдачи карточки
    def category_search(self,category):
        result = self.cursor.execute("""SELECT prod_id,name_product,category,price_product,description,photo FROM products WHERE category like ? """,(category,))
        return result.fetchall()

    #Поиск категорий товаров для генерации кнопок с категориями
    def category(self):
        result = self.conn.execute("""SELECT category FROM products""")
        list_cat = []
        for i in result.fetchall():
            list_cat.append(i[0])
            list_cat = sorted(list(set(list_cat)))
        return list_cat

    #Проверка наличия товара в корзине
    def prod_cart_exists(self,user_id,data):
        result = self.cursor.execute("""SELECT prod_id FROM cart WHERE tg_id = ? AND prod_id = ? """, (user_id,data,))
        return bool(len(result.fetchall()))

    #Проверка наличия в корзине пользователя
    def user_cart_exists(self,user_id):
        result = self.cursor.execute("""SELECT prod_id FROM cart WHERE tg_id = ? """, (user_id,))
        return bool(len(result.fetchall()))

    #Добавление в корзину
    def add_to_cart(self,user_id,data):
        self.cursor.execute("""INSERT INTO cart (tg_id,prod_id) VALUES (?,?) """, (user_id,data,))
        return self.conn.commit()

    #Получение кол-ва товара в корзине
    def count_to_cart(self,user_id,data):
        result = self.cursor.execute("""SELECT count FROM cart WHERE tg_id = ? AND prod_id = ? """, (user_id,data,))
        return result.fetchone()

    #Обновление(Уменьшение или увелечение) кол-ва товара в корзине
    def update_cart(self,user_id,data,count):
        self.cursor.execute("""UPDATE cart SET count = ? WHERE tg_id = ? AND prod_id = ? """, (count,user_id,data,))
        return self.conn.commit()

    #Удаление товара из корзины
    def delete_cart(self,user_id,data):
        self.cursor.execute("""DELETE FROM cart WHERE tg_id = ? AND prod_id = ? """, (user_id,data,))
        return self.conn.commit()

    #Поиск информации товара для карточки корзины
    def product_search(self,user_id):
        result = self.cursor.execute("""SELECT products.prod_id,name_product,category,price_product,description,photo FROM products
        INNER JOIN cart
        ON products.prod_id = cart.prod_id
        WHERE cart.tg_id like ?""", (user_id,))
        return result.fetchall()

    def product_search_id(self,user_id):
        result = self.cursor.execute("""SELECT products.prod_id,name_product,category,price_product,description,photo FROM products
        WHERE tg_id like ?""", (user_id,))
        return result.fetchall()

    #Получение цены*кол-во каждого товара в корзине
    def price_cart(self,user_id):
        result = self.cursor.execute("""SELECT price_product*cart.count FROM products
        INNER JOIN cart 
        ON products.prod_id = cart.prod_id
        WHERE cart.tg_id like ? """, (user_id,))
        return result.fetchall()

    #Информация о пользователе при оформлении заказа
    def info_user(self,user_id):
        result = self.cursor.execute("""SELECT first_name,last_name,address,phone FROM user WHERE tg_id = ? """, (user_id,))
        return result.fetchone()

    #Добавление товаров из корзины в заказы и удаление товаров из корзины
    def cart_to_order(self,user_id,delivery):
        id_order = self.cursor.execute("""SELECT MAX(id_order)+1 FROM user_order""")
        max_id = id_order.fetchone()[0]
        cart = self.cursor.execute("""SELECT prod_id,count FROM cart
        WHERE tg_id like ? """, (user_id,))
        for i in cart.fetchall():
            try:
                self.cursor.execute("""INSERT INTO user_order (tg_id,prod_id,count,delivery,id_order) VALUES (?,?,?,?,?) """, (user_id,i[0],i[1],delivery,max_id,))
            except:
                #Выполняется 1 раз если нету id_order создает дефолт значение
                self.cursor.execute("""INSERT INTO user_order (tg_id,prod_id,count,delivery) VALUES (?,?,?,?) """, (user_id,i[0],i[1],delivery,))
                id_order = self.cursor.execute("""SELECT MAX(id_order) FROM user_order""")
                max_id = id_order.fetchone()[0]
            self.cursor.execute("""DELETE FROM cart WHERE tg_id like ?""", (user_id,))
        return self.conn.commit(), max_id

    #Проверка активных заказов у пользователя
    def order_exists(self,user_id):
        result = self.cursor.execute("""SELECT tg_id FROM user_order WHERE tg_id = ? AND status != 'Завершен' """, (user_id,))
        return bool(len(result.fetchall()))

    #Поиск всех id_order для отправки пользовател. и формирования карточки с заказами
    def search_order_id(self,user_id):
        result = self.cursor.execute("""SELECT id_order,status FROM user_order WHERE tg_id = ? AND status != 'Завершен' """, (user_id,))
        return result.fetchall()

    #Получение заказов для обработки
    def order(self,user_id,id_order):
        result = self.cursor.execute("""SELECT user_order.id,products.prod_id,name_product,price_product,photo,user_order.count,user_order.status,user_order.delivery,user_order.id_order FROM products
        INNER JOIN user_order
        ON products.prod_id = user_order.prod_id
        WHERE user_order.tg_id like ? AND id_order like ? """, (user_id, id_order))
        return result.fetchall()



#Некоторые функции для админ чата
    #Проверка есть ли администратор в базе
    def admin_exists(self,user_id):
        result = self.cursor.execute("""SELECT tg_id FROM admin WHERE tg_id = ?""", (user_id,))
        return bool(len(result.fetchall()))

    #Поиск и вычада всех заказов для обработки
    def search_all_order(self):
        result = self.cursor.execute("""SELECT tg_id,id_order,status FROM user_order WHERE status != 'Завершен' """)
        return result.fetchall()

    #Поиск определенного заказа для выдачи карточки
    def search_order_id_order(self,id_order):
        result = self.cursor.execute("""SELECT user_order.id,products.prod_id,name_product,price_product,photo,user_order.count,user_order.status,user_order.delivery,user_order.id_order,user_order.tg_id FROM products
                INNER JOIN user_order
                ON products.prod_id = user_order.prod_id
                WHERE id_order like ? """, (id_order,))
        return result.fetchall()

    #Получение статуса администратора
    def admin_status(self,user_id):
        result = self.cursor.execute("""SELECT right FROM admin WHERE tg_id = ? """, (user_id,))
        return result.fetchone()

    #Обновление статуса заказа
    def change_status_order(self, id_order, status):
        self.cursor.execute("""UPDATE user_order SET status = ? WHERE id_order like ? """, (status, id_order,))
        return self.conn.commit()

    #Поиск всех администраторов
    def search_admin(self):
        result = self.cursor.execute("""SELECT tg_id, name_admin, right FROM admin WHERE right != 'Продавец' """)
        return result.fetchall()

    #Поиск всех продавцов
    def search_seller(self):
        result = self.cursor.execute("""SELECT tg_id, name_admin, right FROM admin WHERE right = 'Продавец' """)
        return result.fetchall()

    #Поиск администратора для его изменения
    def search_admin_for_id(self, user_id):
        result = self.cursor.execute("""SELECT tg_id, name_admin, right FROM admin WHERE tg_id = ? """, (user_id,))
        return result.fetchall()

    #Изменение имя для Администратора
    def change_name_admin(self, name, user_id):
        self.cursor.execute("""UPDATE admin SET name_admin = ? WHERE tg_id = ? """, (name, user_id))
        return self.conn.commit()


    def delete_admin(self, user_id):
        self.cursor.execute("""DELETE FROM admin WHERE tg_id = ? """, (user_id,))
        return self.conn.commit()

    def add_admin(self, user_id, name, right):
        self.cursor.execute("""INSERT INTO admin (tg_id,name_admin,right) VALUES (?,?,?) """, (user_id, name, right,))
        return self.conn.commit()

    def update_right_admin(self,user_id,right):
        self.cursor.execute("""UPDATE admin SET right WHERE tg_id = ? """, (user_id,right,))
        return self.conn.commit()
