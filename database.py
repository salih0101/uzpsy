import sqlite3

connection = sqlite3.connect('uzpsycho.db')
sql = connection.cursor()


def add_user(user_id, name, phone_number, time_sub, end_sub, gender, status, amount_s):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()

    sql.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?);',
                (user_id, name, phone_number, time_sub, end_sub, gender, status, amount_s))
    connection.commit()
    return add_user


def check_user(user_id):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()
    checker = sql.execute('SELECT user_id, amount_sub FROM users WHERE user_id=?;', (user_id,))

    if checker.fetchone():
        return True
    else:
        return False



def change_name(user_id, name):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()

    sql.execute('UPDATE users SET name=? WHERE user_id=?;', (name['name'], user_id))
    connection.commit()


def change_number(user_id, phone_number):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()

    sql.execute('UPDATE users SET phone_number=? WHERE user_id=?;', (phone_number['phone_number'], user_id))
    connection.commit()




def set_status(user_id, status):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()

    if connection:
        # Сначала удалим старую запись, если она существует
        sql.execute("DELETE FROM user_status WHERE user_id=?", (user_id,))
        connection.commit()

        # Теперь установим новое значение статуса
        sql.execute("INSERT INTO user_status (user_id, status) VALUES (?, ?)", (user_id, status))
        connection.commit()

    elif not connection:
        print("Ошибка при подключении к базе данных")



def update_status(user_id):
    # Устанавливаем соединение с базой данных с помощью менеджера контекста (оператор with)
    with sqlite3.connect('uzpsycho.db') as connection:
        # Создаем курсор с использованием соединения
        sql = connection.cursor()

        # Проверяем, существует ли запись с указанным user_id
        sql.execute("SELECT status FROM user_status WHERE user_id = ?", (user_id,))
        result = sql.fetchone()

        if result:
            # Если запись существует, получаем текущий статус
            current_status = result[0]
            # Вычисляем новый статус
            new_status = current_status + 1
            # Обновляем статус в таблице
            sql.execute("UPDATE user_status SET status = ? WHERE user_id = ?", (new_status, user_id))
        else:
            # Если записи нет, создаем новую с начальным статусом (например, статус 0)
            sql.execute("INSERT INTO user_status (user_id, status) VALUES (?, ?)", (user_id, 0))

        connection.commit()




def get_status(user_id):
    connection = sqlite3.connect('uzpsycho.db')
    sql = connection.cursor()

    if connection:
        sql.execute("SELECT status FROM user_status WHERE user_id = ?", (user_id,))
        result = sql.fetchone()
        current_status = result[0] if result else 0

        connection.close()
        return current_status
    elif not connection:
        print("Ошибка при подключении к базе данных")



# sql.execute('CREATE TABLE users(user_id integer, name text, phone_number text, time_sub datetime, end_sub datetime, gender text, status text, amount_sub integer);')
# sql.execute('CREATE TABLE paid(user_id integer, name text, phone_number text, time_sub datetime, end_sub datetime, gender text, status text, amount_sub integer);')
sql.execute('CREATE TABLE user_status(user_id integer, status integer);')

# def get_status(user_id):
#     try:
#         connection = sqlite3.connect('uzpsycho.db')
#         sql = connection.cursor()
#
#
#         sql.execute("SELECT status FROM user_status WHERE user_id = ?", (user_id,))
#         result = sql.fetchone()
#         current_status = result[0] if result else 0
#
#         return current_status
#
#     except sqlite3.Error as e:
#         print(f"Ошибка при получении статуса: {e}")

# def set_status(user_id, status):
#     try:
#         connection = sqlite3.connect('uzpsycho.db')
#         sql = connection.cursor()
#
#         # Сначала удалим старую запись, если она существует
#         sql.execute("DELETE FROM user_status WHERE user_id=?", (user_id,))
#
#         # Теперь установим новое значение статуса
#         sql.execute("INSERT INTO user_status (user_id, status) VALUES (?, ?)", (user_id, status))
#         connection.commit()
#
#     except sqlite3.Error as e:
#         print(f"Ошибка при установке статуса: {e}")
