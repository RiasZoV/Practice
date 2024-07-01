from manage_users import (
    add_user, add_role, add_function, list_subordinates, change_password,
    change_user_role, delete_user, list_users, change_subordinates
)
from auth import login_user, change_own_password
from session_management import get_session
from database import Role, User, Function


def admin_actions(user):
    while True:
        action = input(
            "Выберите действие (add/delete/change_role/list/change_password/change_subordinates/logout): ").strip().lower()
        if action == "add":
            new_login = input("Введите логин нового пользователя: ").strip()
            new_password = input("Введите пароль нового пользователя: ").strip()
            new_role = input("Введите роль нового пользователя: ").strip()
            age = int(input("Введите возраст нового пользователя: ").strip())
            add_user(new_login, new_password, new_role, age)
        elif action == "delete":
            user_id = int(input("Введите ID пользователя для удаления: ").strip())
            delete_user(user_id)
        elif action == "change_role":
            user_id = int(input("Введите ID пользователя для изменения роли: ").strip())
            new_role = input("Введите новую роль: ").strip()
            change_user_role(user_id, new_role)
        elif action == "list":
            list_users()
        elif action == "change_password":
            user_id = int(input("Введите ID пользователя для смены пароля: ").strip())
            new_password = input("Введите новый пароль: ").strip()
            change_password(user_id, new_password)
        elif action == "change_subordinates":
            user_id = int(input("Введите ID пользователя для изменения подчиненных: ").strip())
            subordinates_logins = input("Введите логины новых подчиненных через запятую: ").strip().split(',')
            change_subordinates(user_id, [login.strip() for login in subordinates_logins])
        elif action == "logout":
            print("Выход из системы.")
            break
        else:
            print("Неизвестное действие. Попробуйте снова.")
    return False  # Return to indicate logout


def manager_actions(user):
    while True:
        action = input("Выберите действие (list_subordinates/change_password/logout): ").strip().lower()
        if action == "list_subordinates":
            list_subordinates(user.id)
        elif action == "change_password":
            subordinate_id = int(input("Введите ID подчиненного для смены пароля: ").strip())
            new_password = input("Введите новый пароль: ").strip()
            change_password(subordinate_id, new_password)
        elif action == "logout":
            print("Выход из системы.")
            break
        else:
            print("Неизвестное действие. Попробуйте снова.")
    return False  # Return to indicate logout


def user_actions(user):
    while True:
        action = input("Выберите действие (view_profile/change_password/logout): ").strip().lower()
        if action == "view_profile":
            view_profile(user)
        elif action == "change_password":
            old_password = input("Введите старый пароль: ").strip()
            new_password = input("Введите новый пароль: ").strip()
            change_own_password(user.id, old_password, new_password)
        elif action == "logout":
            print("Выход из системы.")
            break
        else:
            print("Неизвестное действие. Попробуйте снова.")
    return False  # Return to indicate logout


def view_profile(user):
    """Просмотр профиля пользователя"""
    print(f"Профиль пользователя:\nЛогин: {user.login}\nВозраст: {user.age}")


def initialize_database():
    """Добавление ролей и функций только при первом запуске"""
    session = get_session()

    # Проверка, существуют ли уже роли и функции
    if not session.query(Role).first():
        add_role('Пользователь')
        add_role('Руководитель')
        add_role('Админ')

    if not session.query(Function).first():
        add_function('Просмотр данных', 1, 'Пользователь')
        add_function('Редактирование данных', 2, 'Руководитель')
        add_function('Управление пользователями', 3, 'Админ')

    session.close()


def add_initial_users():
    """Добавление начальных пользователей только при первом запуске"""
    session = get_session()
    if not session.query(User).first():
        print("Заполнение базы данных начальными пользователями...")
        while True:
            login = input("Введите логин пользователя: ").strip()
            password = input("Введите пароль пользователя: ").strip()
            role = input("Введите роль пользователя (Пользователь, Руководитель, Админ): ").strip()
            age = int(input("Введите возраст пользователя: ").strip())
            subordinates_input = None
            if role in ['Руководитель', 'Админ']:
                subordinates_input = input(
                    "Введите логины подчиненных пользователей через запятую (если есть): ").strip()
            subordinates = [s.strip() for s in subordinates_input.split(',')] if subordinates_input else None

            add_user(login, password, role, age, subordinates)

            another = input("Хотите добавить еще одного пользователя? (да/нет): ").strip().lower()
            if another != 'да':
                break
    session.close()


if __name__ == "__main__":
    initialize_database()
    add_initial_users()

    while True:
        login = input("Введите логин для входа: ").strip()
        password = input("Введите пароль для входа: ").strip()
        user = login_user(login, password)
        if user:
            if user.role_id == 1:  # Пользователь
                if not user_actions(user):
                    next_action = input(
                        "Введите 'exit' для выхода из программы или 'login' для входа под другим пользователем: ").strip().lower()
                    if next_action == 'exit':
                        print("Программа завершена.")
                        break
            elif user.role_id == 2:  # Руководитель
                if not manager_actions(user):
                    next_action = input(
                        "Введите 'exit' для выхода из программы или 'login' для входа под другим пользователем: ").strip().lower()
                    if next_action == 'exit':
                        print("Программа завершена.")
                        break
            elif user.role_id == 3:  # Админ
                if not admin_actions(user):
                    next_action = input(
                        "Введите 'exit' для выхода из программы или 'login' для входа под другим пользователем: ").strip().lower()
                    if next_action == 'exit':
                        print("Программа завершена.")
                        break
        else:
            print("Не удалось войти. Попробуйте снова.")