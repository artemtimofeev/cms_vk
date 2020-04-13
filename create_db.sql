CREATE TABLE Orders (
  order_id SERIAL NOT NULL ,
  full_name VARCHAR(255)  NOT NULL ,
  address VARCHAR(255)    ,
  contacts VARCHAR(255)    ,
  phone_number VARCHAR(255)    ,
  order_price INTEGER    ,
  status VARCHAR(255)      ,
PRIMARY KEY(order_id));

#  Примеры 

insert into Orders (full_name, address, contacts, phone_number, order_price, status)
values ('Тимофеев Артём Евгеньевич', 'address', 'email@google.com email2@yandex.ru', '+79008003020', 200, 'сборка');

insert into Orders (full_name, address, contacts, phone_number, order_price, status)
values ('Неизвестный Евгений Евгеньевич', 'address', 'email@google.com email2@yandex.ru', '+79008003020', 200, 'сборка');

insert into Orders (full_name, address, contacts, phone_number, order_price, status)
values ('Тимофеев Артём Евгеньевич', 'address', 'email@google.com email2@yandex.ru', '+79008003020', 400, 'сборка');

select * from Orders where order_id = 1;

select * from Orders where full_name = 'Тимофеев Артём Евгеньевич'

update Orders set status = 'завершен' where order_id = 1;




