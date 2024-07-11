from sqlalchemy.orm.exc import NoResultFound
from database import User, Role, Function
from session_management import get_session
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_user_by_login(login):
    session = get_session()
    try:
        user = session.query(User).filter_by(login=login).one()
        return user
    except NoResultFound:
        print(f"Пользователь с логином '{login}' не найден.")
    finally:
        session.close()

def add_user(login, password, role_name, age, subordinates=None):
    """Добавление нового пользователя в бд"""
    session = get_session()
    try:
        if session.query(User).filter_by(login=login).first():
            print(f"Пользователь с логином '{login}' уже существует.")
            session.close()
            return

        role = session.query(Role).filter_by(name=role_name).one()
        hashed_password = hash_password(password)
        new_user = User(login=login, password=hashed_password, age=age, role_id=role.id)
        session.add(new_user)
        session.commit()

        if subordinates and role_name in ['Руководитель', 'Админ']:
            for sub_login in subordinates:
                try:
                    subordinate = session.query(User).filter_by(login=sub_login).one()
                    new_user.subordinates.append(subordinate)
                except NoResultFound:
                    print(f"Подчиненный пользователь '{sub_login}' не найден.")
            session.commit()

        print(f"Пользователь {login} добавлен.")
    except NoResultFound:
        print(f"Роль '{role_name}' не найдена.")
    finally:
        session.close()

def add_role(name):
    """Добавление новой роли в бд"""
    session = get_session()
    if session.query(Role).filter_by(name=name).first():
        print(f"Роль '{name}' уже существует.")
        session.close()
        return
    new_role = Role(name=name)
    session.add(new_role)
    session.commit()
    print(f"Роль {name} добавлена.")
    session.close()

def add_function(name, access_level, role_name):
    """Добавление новой функции в бд"""
    session = get_session()
    try:
        role = session.query(Role).filter_by(name=role_name).one()
        if session.query(Function).filter_by(name=name, role_id=role.id).first():
            print(f"Функция '{name}' для роли '{role_name}' уже существует.")
            session.close()
            return
        new_function = Function(name=name, access_level=access_level, role_id=role.id)
        session.add(new_function)
        session.commit()
        print(f"Функция {name} с уровнем доступа {access_level} добавлена для роли {role_name}.")
    except NoResultFound:
        print(f"Роль '{role_name}' не найдена.")
    finally:
        session.close()

def list_roles():
    """Вывод списка всех ролей"""
    session = get_session()
    roles = session.query(Role).all()
    session.close()
    return roles

def get_role_by_number(number):
    """Получение роли по номеру"""
    roles = list_roles()
    if 1 <= number <= len(roles):
        return roles[number - 1]
    else:
        print(f"Неправильный номер роли: {number}")
        return None

def list_subordinates(user_id):
    """Вывод списка подчиненных для пользователя"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        subordinates = user.subordinates
        for sub in subordinates:
            print(f"Подчиненный: {sub.login}")
    except NoResultFound:
        print(f"Пользователь с ID {user_id} не найден.")
    finally:
        session.close()

def change_password(user_id, new_password):
    """Изменение пароля для пользователя"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        user.password = hash_password(new_password)
        session.commit()
        print(f"Пароль для пользователя {user.login} изменен.")
    except NoResultFound:
        print(f"Пользователь с ID {user_id} не найден.")
    finally:
        session.close()

def change_user_role(user_id, new_role_name):
    """Изменение роли пользователя"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        new_role = session.query(Role).filter_by(name=new_role_name).one()
        user.role_id = new_role.id
        session.commit()
        print(f"Роль для пользователя {user.login} изменена на {new_role_name}.")
    except NoResultFound:
        print(f"Пользователь или роль не найдены.")
    finally:
        session.close()

def delete_user(user_id):
    """Удаление пользователя"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        session.delete(user)
        session.commit()
        print(f"Пользователь {user.login} удален.")
    except NoResultFound:
        print(f"Пользователь с ID {user_id} не найден.")
    finally:
        session.close()

def list_users():
    """Вывод списка всех пользователей"""
    session = get_session()
    users = session.query(User).all()
    for user in users:
        print(f"Пользователь: {user.login}, Роль: {user.role_id}, Возраст: {user.age}")
    session.close()

def change_subordinates(user_id, new_subordinates_logins):
    """Изменение списка подчиненных пользователя"""
    session = get_session()
    try:
        user = session.query(User).filter_by(id=user_id).one()
        user.subordinates = []
        for login in new_subordinates_logins:
            subordinate = session.query(User).filter_by(login=login).one()
            user.subordinates.append(subordinate)
        session.commit()
        print(f"Список подчиненных для пользователя {user.login} обновлен.")
    except NoResultFound:
        print(f"Пользователь или подчиненные не найдены.")
    finally:
        session.close()



