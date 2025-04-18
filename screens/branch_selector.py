from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
import requests
from config import API_URL

class BranchSelectionScreen(QWidget):
    def __init__(self, token, on_branch_selected):
        super().__init__()
        self.token = token
        self.on_branch_selected = on_branch_selected
        self.layout = QVBoxLayout(self)

        self.layout.addWidget(QLabel("Seleccione la sucursal"))
        self.branch_selector = QComboBox()
        self.layout.addWidget(self.branch_selector)

        self.continue_btn = QPushButton("Continuar")
        self.continue_btn.clicked.connect(self.select_branch)
        self.layout.addWidget(self.continue_btn)

        self.status = QLabel("")
        self.layout.addWidget(self.status)

        self.load_branches()

    def load_branches(self):
        try:
            res = requests.get(f"{API_URL}/branch", headers={
                "Authorization": f"Bearer {self.token}"
            })
            res.raise_for_status()
            branches = res.json()
            for b in branches:
                self.branch_selector.addItem(f"{b['branchName']}", (b['id'], b['branchName']))
        except Exception as e:
            self.status.setText("Error al cargar sucursales: " + str(e))

    def select_branch(self):
        branch_id, branch_name = self.branch_selector.currentData()
        self.on_branch_selected(self.token, branch_id, branch_name)
