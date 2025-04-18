from PyQt6.QtWidgets import QWidget, QStackedLayout
from session_manager import load_token
from screens.login import LoginScreen
from screens.branch_selector import BranchSelectionScreen
from screens.printer import PrintScreen

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impresora POS - ChamaFruit")
        self.resize(420, 600)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        token = load_token()
        if token:
            self.on_login_success(token)
        else:
            self.login_screen = LoginScreen(self.on_login_success)
            self.stack.addWidget(self.login_screen)

    def on_login_success(self, token):
        self.branch_screen = BranchSelectionScreen(token, self.on_branch_selected)
        self.stack.addWidget(self.branch_screen)
        self.stack.setCurrentWidget(self.branch_screen)

    def on_branch_selected(self, token, branch_id, branch_name):
        self.print_screen = PrintScreen(token, branch_id, branch_name)
        self.stack.addWidget(self.print_screen)
        self.stack.setCurrentWidget(self.print_screen)

