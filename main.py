import psycopg2
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random

message_order = "Id заказа: {}\n" \
                "ФИО покупателя: {}\n" \
                "адрес: {}\n" \
                "контакты: {}\n" \
                "телефонный номер: {}\n" \
                "сумма заказа: {}\n" \
                "статус: {}\n\n"


class Message(object):
    def __init__(self, handler):
        self.user_id = handler.user_id
        self.text = ""
        self.attachments = ""
        random.seed()
        self.random_id = random.randint(1, 2 ** 64)
        self.keyboard = 0

    def set_text(self, text):
        self.text = text

    def set_keyboard(self, keyboard):
        self.keyboard = keyboard

    def get_message(self):
        if self.keyboard != 0:
            parameters = {'user_id': self.user_id,
                          'random_id': self.random_id,
                          'message': self.text,
                          'attachment': self.attachments,
                          'keyboard': self.keyboard.get_keyboard()}
        else:
            parameters = {'user_id': self.user_id,
                          'random_id': self.random_id,
                          'message': self.text,
                          'attachment': self.attachments}
        return parameters


class Handler(object):
    def __init__(self, user_id):
        self.status = "login"
        self.user_id = user_id
        self.keys = {'Timofeev': 'qwerty123'}

    def new_message(self, message):
        if self.status == "login":
            return self.login(message)

        if self.status == "main_menu":
            if message == "Получить инфо по id заказа":
                return self.handler_get_info()
            if message == "Изменить статус заказа":
                return self.handler_set_status()
            if message == "Проверить все заказы на ФИО":
                return self.handler_check_full_name()
            if message == "Создать новый заказ":
                return self.handler_new_order()

        if self.status == "get_info":
            return self.handler_get_info_data(message)

        if self.status == "set_status":
            return self.handler_set_status_data(message)

        if self.status == "check_full_name":
            return self.handler_check_full_name_data(message)

        if self.status == "new_order":
            return self.handler_new_order_data(message)

        return self.handler_error()

    def handler_get_info_data(self, message):
        id = message.split()[0]

        conn = psycopg2.connect(host="localhost", user="postgres", password="12344321", dbname="postgres")
        cursor = conn.cursor()

        cursor.execute("select * from Orders where order_id = %s", (id, ))
        results = cursor.fetchall()

        conn.commit()
        conn.close()

        mess = Message(self)
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Получить инфо по id заказа', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Изменить статус заказа', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Проверить все заказы на ФИО', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Создать новый заказ', color=VkKeyboardColor.POSITIVE)

        mess.set_keyboard(keyboard)

        if len(results) == 0:
            mess.set_text("Заказ с таким id не найден")
        else:
            mess.set_text(message_order.format(results[0][0],
                                               results[0][1],
                                               results[0][2],
                                               results[0][3],
                                               results[0][4],
                                               results[0][5],
                                               results[0][6]))

        self.status = "main_menu"

        return mess.get_message()

    def handler_set_status_data(self, message):
        id, new_status = message.split()

        conn = psycopg2.connect(host="localhost", user="postgres", password="12344321", dbname="postgres")
        cursor = conn.cursor()

        cursor.execute("update Orders set status = %s where order_id = %s;", (new_status, id))

        conn.commit()
        conn.close()

        mess = Message(self)
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Получить инфо по id заказа', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Изменить статус заказа', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Проверить все заказы на ФИО', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Создать новый заказ', color=VkKeyboardColor.POSITIVE)

        mess.set_keyboard(keyboard)
        mess.set_text("Успешно обновлено")

        self.status = "main_menu"

        return mess.get_message()

    def handler_check_full_name_data(self, message):
        full_name = message

        conn = psycopg2.connect(host="localhost", user="postgres", password="12344321", dbname="postgres")
        cursor = conn.cursor()

        cursor.execute("select * from Orders where full_name = %s", (full_name,))
        results = cursor.fetchall()

        conn.commit()
        conn.close()

        mess = Message(self)
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Получить инфо по id заказа', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Изменить статус заказа', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Проверить все заказы на ФИО', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Создать новый заказ', color=VkKeyboardColor.POSITIVE)

        mess.set_keyboard(keyboard)

        if len(results) == 0:
            mess.set_text("Заказов с таким ФИО не найдено")
        else:
            result = ""
            for i in range(len(results)):
                result += message_order.format(results[i][0],
                                               results[i][1],
                                               results[i][2],
                                               results[i][3],
                                               results[i][4],
                                               results[i][5],
                                               results[i][6])
            mess.set_text(result)

        self.status = "main_menu"

        return mess.get_message()

    def handler_new_order_data(self, message):
        full_name, address, contacts, phone_number, order_price = message.split(',')
        status = 'обработка'

        conn = psycopg2.connect(host="localhost", user="postgres", password="12344321", dbname="postgres")
        cursor = conn.cursor()

        cursor.execute("insert into Orders (full_name, address, contacts, phone_number, order_price, status) "
                       "values (%s, %s, %s, %s, %s, %s);", (full_name,
                                                            address,
                                                            contacts,
                                                            phone_number,
                                                            order_price,
                                                            status))

        conn.commit()
        conn.close()

        mess = Message(self)
        keyboard = VkKeyboard(one_time=False)
        keyboard.add_button('Получить инфо по id заказа', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Изменить статус заказа', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Проверить все заказы на ФИО', color=VkKeyboardColor.DEFAULT)
        keyboard.add_line()
        keyboard.add_button('Создать новый заказ', color=VkKeyboardColor.POSITIVE)

        mess.set_keyboard(keyboard)
        mess.set_text("Успешно обработано")

        self.status = "main_menu"

        return mess.get_message()

    def handler_get_info(self):
        mess = Message(self)

        mess.set_text("Введите id заказа")

        self.status = "get_info"

        return mess.get_message()

    def handler_set_status(self):
        mess = Message(self)

        mess.set_text("Введите id заказа и его новый статус")

        self.status = "set_status"

        return mess.get_message()

    def handler_check_full_name(self):
        mess = Message(self)

        mess.set_text("Введите ФИО")

        self.status = "check_full_name"

        return mess.get_message()

    def handler_new_order(self):
        mess = Message(self)

        mess.set_text("Введите ФИО покупателя, адрес, контакты, телефонный номер,"
                      " сумму заказа через запятую без пробелов")

        self.status = "new_order"

        return mess.get_message()

    def handler_error(self):
        mess = Message(self)

        mess.set_text("Ошибка")

        return mess.get_message()

    def login(self, message):
        key = message.split()
        if len(key) != 2:
            mess = Message(self)
            mess.set_text("Неправильный формат ввода")
            return mess.get_message()

        login, password = key[0], key[1]

        if login in self.keys:
            if self.keys[login] == password:
                self.status = "main_menu"

                mess = Message(self)
                mess.set_text("Вход в систему выполнен успешно")

                keyboard = VkKeyboard(one_time=False)
                keyboard.add_button('Получить инфо по id заказа', color=VkKeyboardColor.PRIMARY)
                keyboard.add_line()
                keyboard.add_button('Изменить статус заказа', color=VkKeyboardColor.DEFAULT)
                keyboard.add_line()
                keyboard.add_button('Проверить все заказы на ФИО', color=VkKeyboardColor.DEFAULT)
                keyboard.add_line()
                keyboard.add_button('Создать новый заказ', color=VkKeyboardColor.POSITIVE)

                mess.set_keyboard(keyboard)

                return mess.get_message()
        else:
            mess = Message(self)
            mess.set_text("Неверный логин или пароль")

            return mess.get_message()


def main():
    # Создаем подключение
    vk = vk_api.VkApi(token="d514e678358eb9bc016cb44219ae89811c87fca05db874dd2f8d2c8035cbf57a768f2d2654a72f4505dd9")
    longpoll = VkLongPoll(vk)

    # Кэш пользователей
    users = {}
    users_id = {}

    print("Server started")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.user_id not in users_id:

                # Создаем объект обработчика и сохраняем в кэше
                users[event.user_id] = Handler(event.user_id)
                users_id[event.user_id] = True

            answer = users[event.user_id].new_message(event.text)
            vk.method('messages.send', answer)


if __name__ == "__main__":
    main()
