import sys
import datetime
from abc import ABC, abstractmethod
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt


class BaseEntity(ABC):
    """Абстрактный базовый класс для всех сущностей."""

    @abstractmethod
    def get_display_info(self) -> str:
        pass


class User(BaseEntity):
    """Класс пользователя."""

    def __init__(self, login: str, time_in: datetime.datetime = None, time_out: datetime.datetime = None):
        self._login = login
        self._time_in = time_in if time_in else datetime.datetime.now()
        self._time_out = time_out

    @property
    def login(self):
        return self._login

    @login.setter
    def login(self, value):
        if not value:
            raise ValueError("Логин не может быть пустым")
        self._login = value

    @property
    def time_in(self):
        return self._time_in

    @time_in.setter
    def time_in(self, value):
        self._time_in = value

    @property
    def time_out(self):
        return self._time_out

    @time_out.setter
    def time_out(self, value):
        self._time_out = value

    def __str__(self):
        return f"User({self._login})"

    def __repr__(self):
        return f"User(login='{self._login}', in='{self._time_in}', out='{self._time_out}')"

    def __eq__(self, other):
        if not isinstance(other, User):
            return NotImplemented
        return self._login == other._login

    def get_display_info(self) -> str:
        return self._login


class CustomStorage:
    """Кастомный класс для хранения данных без dict."""

    def __init__(self):
        self._data = []

    def add(self, key, value):
        for index, (existing_key, _) in enumerate(self._data):
            if existing_key == key:
                self._data[index] = (key, value)
                return value
        self._data.append((key, value))
        return value

    def get(self, key):
        for k, v in self._data:
            if k == key:
                return v
        return None

    def get_all(self):
        return list(self._data)


class CustomLabel(QLabel):
    """Переопределенный компонент окна."""

    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("font-weight: bold; color: #333;")


class CustomLineEdit(QLineEdit):
    """Переопределенный компонент окна."""

    def __init__(self, placeholder):
        super().__init__()
        self.setPlaceholderText(placeholder)


class CustomButton(QPushButton):
    """Переопределенный компонент окна."""

    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)


class CustomTable(QTableWidget):
    """Переопределенный компонент окна."""

    def __init__(self, rows, cols):
        super().__init__(rows, cols)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


class CustomHeader(QLabel):
    """Переопределенный компонент окна."""

    def __init__(self, text):
        super().__init__(text)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("font-size: 18px; margin-bottom: 10px;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система учета посещаемости")
        self.resize(800, 600)

        self.storage = CustomStorage()
        self.current_user = None
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        header = CustomHeader("Учет рабочего времени")
        layout.addWidget(header)

        form_layout = QHBoxLayout()
        self.login_label = CustomLabel("Логин:")
        self.login_input = CustomLineEdit("Введите имя пользователя")

        self.btn_login = CustomButton("Вход (Login)")
        self.btn_login.clicked.connect(self.handle_login)

        self.btn_logout = CustomButton("Выход (Logout)")
        self.btn_logout.clicked.connect(self.handle_logout)
        self.btn_logout.setEnabled(False)
        self.btn_logout.setStyleSheet("background-color: #f44336; color: white;")

        form_layout.addWidget(self.login_label)
        form_layout.addWidget(self.login_input)
        form_layout.addWidget(self.btn_login)
        form_layout.addWidget(self.btn_logout)
        layout.addLayout(form_layout)

        self.table = CustomTable(0, 3)
        self.table.setHorizontalHeaderLabels(["Login", "Time In", "Time Out"])
        layout.addWidget(self.table)

        self.btn_fill = CustomButton("Сгенерировать 10 тестовых записей")
        self.btn_fill.clicked.connect(self.generate_test_data)
        layout.addWidget(self.btn_fill)

        self.update_table()

    def handle_login(self):
        login = self.login_input.text().strip()
        if not login:
            QMessageBox.warning(self, "Ошибка", "Введите логин!")
            return

        if self.storage.get(login):
            QMessageBox.warning(self, "Ошибка", f"Пользователь с логином '{login}' уже существует.")
            return

        user = User(login)
        self.storage.add(login, user)
        self.current_user = user

        self.login_input.setEnabled(False)
        self.btn_login.setEnabled(False)
        self.btn_logout.setEnabled(True)

        self.update_table()

    def handle_logout(self):
        if self.current_user:
            self.current_user.time_out = datetime.datetime.now()
            self.current_user = None

            self.login_input.setEnabled(True)
            self.btn_login.setEnabled(True)
            self.btn_logout.setEnabled(False)
            self.login_input.clear()

            self.update_table()

    def generate_test_data(self):
        """Генерирует 10 объектов для выполнения требования."""
        for i in range(1, 101):
            login = f"User_{i}"
            if self.storage.get(login):
                continue

            t_in = datetime.datetime.now() - datetime.timedelta(hours=i)
            t_out = t_in + datetime.timedelta(minutes=30)
            user = User(login, t_in, t_out)
            self.storage.add(login, user)

            if len(self.storage.get_all()) >= 10:
                break

        final_count = len(self.storage.get_all())
        self.update_table()
        QMessageBox.information(self, "Успех", f"Добавлено {final_count} тестовых пользователей.")

    def update_table(self):
        """Обновление UI таблицы."""
        data = self.storage.get_all()
        self.table.setRowCount(len(data))

        for row, (_, user) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(user.login))
            t_in_str = user.time_in.strftime("%d.%m.%Y %H:%M:%S") if user.time_in else "-"
            self.table.setItem(row, 1, QTableWidgetItem(t_in_str))
            t_out_str = user.time_out.strftime("%d.%m.%Y %H:%M:%S") if user.time_out else "-"
            self.table.setItem(row, 2, QTableWidgetItem(t_out_str))

    @staticmethod
    def format_report(data):
        """Формирует текстовый отчет из списка пользователей."""
        w_login = 10
        w_time = 20

        header = f"+{'-' * (w_login + 2)}+{'-' * (w_time + 2)}+{'-' * (w_time + 2)}+"
        titles = f"| {'login':^{w_login}} | {'time_in':^{w_time}} | {'time_out':^{w_time}} |"
        lines = [header, titles, header]

        for _, user in data:
            login = user.login
            t_in = user.time_in.strftime("%d.%m.%Y %H:%M:%S") if user.time_in else "N/A"
            t_out = user.time_out.strftime("%d.%m.%Y %H:%M:%S") if user.time_out else "N/A"
            line = f"| {login:<{w_login}} | {t_in:<{w_time}} | {t_out:<{w_time}} |"
            lines.append(line)

        lines.append(header)
        return "\n".join(lines)

    def closeEvent(self, event):
        """Событие закрытия окна. Сохраняем отчет."""
        self.save_report()
        event.accept()

    def save_report(self):
        """Метод экземпляра для сохранения."""
        filename = "report.txt"
        data = self.storage.get_all()

        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.format_report(data))
            print(f"Отчет сохранен в {filename}")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
