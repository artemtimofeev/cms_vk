# cms_vk

Перед началом работы в системе, пользователь должен ввести логин и пароль.
После входа в систему, у пользователю доступны 4 функции:
  1. Получить информацию о заказе по id заказа
  2. Изменить статус заказа по id заказа
  3. Просмотреть все заказы по ФИО
  4. Создать новый заказ
  
В основном цикле прослушивания LongPoll сервера когда приходит новое сообщение, то для пользователя создается обьект Handler() (только если не был создан до этого), у которого есть метод new_message(message: str) -> answer: dict. (answer -- это объект с параметрами сообщения, помимо текста и id получателя, он содержит объект клавиатуры). Затем, пользователь получает answer.
Handler() взаимодействует с СУБД.

Демонстрация работы: https://youtu.be/xXjDGUI30CE
