from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QCheckBox, QSpacerItem, QSizePolicy
)
import requests
from config import API_URL
from session_manager import save_token

class LoginScreen(QWidget):
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)

        self.setStyleSheet("QLineEdit, QPushButton { font-size: 14px; }")

        self.layout.addWidget(QLabel("Usuario"))
        self.username_input = QLineEdit()
        self.layout.addWidget(self.username_input)

        self.layout.addWidget(QLabel("Contraseña"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.remember_checkbox = QCheckBox("Recordar sesión")
        self.layout.addWidget(self.remember_checkbox)

        self.login_btn = QPushButton("Iniciar sesión")
        self.login_btn.clicked.connect(self.login)
        self.layout.addWidget(self.login_btn)

        self.message_label = QLabel("")
        self.layout.addWidget(self.message_label)

        self.layout.addItem(QSpacerItem(0, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            res = requests.post(f"{API_URL}/auth/login", json={
                "username": username,
                "password": password
            }, headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            })
            res.raise_for_status()
            token = res.json()["token"]
            if self.remember_checkbox.isChecked():
                save_token(token)
            self.on_login_success(token)
        except Exception as e:
            self.message_label.setText("Inicio de sesión falló: " + str(e))
