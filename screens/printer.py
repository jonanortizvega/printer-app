import time
import serial
import requests
import textwrap
from serial.tools import list_ports
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QHBoxLayout, QComboBox
from config import API_URL

class PrintScreen(QWidget):
    def __init__(self, token, branch_id, branch_name):
        super().__init__()
        self.token = token
        self.branch_id = branch_id
        self.branch_name = branch_name
        self.port = "COM8"

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Sucursal: {branch_name}"))

        layout.addWidget(QLabel("ID de la Venta"))
        self.purchase_input = QLineEdit()
        layout.addWidget(self.purchase_input)

        self.fetch_button = QPushButton("Buscar Venta")
        self.fetch_button.clicked.connect(self.fetch_purchase)
        layout.addWidget(self.fetch_button)

        self.receipt_preview = QTextEdit(readOnly=True)
        layout.addWidget(self.receipt_preview)

        btn_row = QHBoxLayout()
        self.print_button = QPushButton("Imprimir")
        self.print_button.clicked.connect(self.print_receipt)
        btn_row.addWidget(self.print_button)

        self.port_selector = QComboBox()
        available_ports = [port.device for port in list_ports.comports()]
        if "COM8" in available_ports:
            self.port = "COM8"
        self.port_selector.addItems(available_ports)
        self.port_selector.currentIndexChanged.connect(self.change_port)
        btn_row.addWidget(self.port_selector)

        layout.addLayout(btn_row)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        self.test_button = QPushButton("Test de Ancho")
        self.test_button.clicked.connect(self.test_width)
        btn_row.addWidget(self.test_button)


    def change_port(self):
        self.port = self.port_selector.currentText()

    def fetch_purchase(self):
        purchase_id = self.purchase_input.text()
        try:
            res = requests.get(
                f"{API_URL}/branch/{self.branch_id}/purchases/{purchase_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            res.raise_for_status()
            purchase = res.json()
            receipt = self.generate_text_receipt(purchase)
            self.receipt_preview.setPlainText(receipt)
        except Exception as e:
            self.receipt_preview.setPlainText("Error: " + str(e))

    def print_receipt(self):
        text = self.receipt_preview.toPlainText()
        try:
            ser = serial.Serial(self.port, baudrate=9600, timeout=1)
            time.sleep(1)
            ser.write(text.encode("utf-8", errors="ignore"))
            time.sleep(1)
            ser.write(b'\n\n\n')
            time.sleep(1)
            ser.write(b'\x1d\x56\x41')  # cut
            ser.close()
            self.status_label.setText("Impresión completada.")
        except Exception as e:
            self.status_label.setText("Error al imprimir: " + str(e))

    def generate_text_receipt(self, p):
        lines = []
        WIDTH = 32
        center = lambda t: t.center(WIDTH)
        right = lambda t: t.rjust(WIDTH)

        lines.append(center("Comprobante de Venta"))
        lines.append("-" * WIDTH)
        lines.append(f"Nro Venta: {p['id']}")
        lines.append(f"Fecha: {p['createdAt'][:16].replace('T',' ')}")
        lines.append("")

        # Cliente
        if p.get("Client"):
            c = p["Client"]
            lines.extend([
                f"Nombre: {c.get('name', 'N/A')}",
                f"RUT: {c.get('rut', 'N/A')}",
                f"Email: {c.get('email', 'N/A')}",
                f"Dirección: {c.get('address', 'N/A')}",
                f"Ciudad: {c.get('city', 'N/A')}",
                f"Teléfono: {c.get('phone', 'N/A')}"
            ])
        else:
            lines.append("Venta sin cliente")

        lines.append("")
        lines.append("Detalle:")

        # 🛒 Items
        for item in p["items"]:
            if item["quantity"] <= 0:
                continue
            name = item["varietyName"]
            qty = item["quantity"]
            price = item["price"]
            unit = item.get("metricUnit") or "u"
            total = qty * price

            # Compose base text line
            item_line = f"{name} x{qty} ({price} c/{unit})"
            wrapped_lines = textwrap.wrap(item_line, width=WIDTH)

            for i, line in enumerate(wrapped_lines):
                if i == len(wrapped_lines) - 1:
                    price_text = f"${total:,.0f}".replace(",", ".")
                    space = WIDTH - len(line)
                    if space >= len(price_text):
                        # Attach price right-aligned
                        line += " " * (space - len(price_text)) + price_text
                    else:
                        lines.append(line)
                        line = price_text.rjust(WIDTH)
                lines.append(line)

        # 🧮 Total
        lines.append("-" * WIDTH)
        total_text = f"Total: ${p['totalAmount']:,.0f}".replace(",", ".")
        lines.append(right(total_text))
        lines.append("")

        # 💳 Pago
        method = p.get("paymentMethod", "No especificado")
        detail = p.get("detailForPayment") or {}

        lines.append("Método de pago: " + method)
        if method == "cheque":
            lines.append("Cheque N°: " + str(detail.get("chequeNumber", "N/A")))
            lines.append("Expira: " + str(detail.get("chequeExpiration", "N/A")))
            if detail.get("initialPayment"):
                lines.append("Abono: $" + str(detail["initialPayment"]))
        elif method in ["tarjeta", "transferencia"]:
            lines.append("Transacción: " + str(detail.get("transactionNumber", "N/A")))
        elif method == "efectivo":
            recibido = int(detail.get("receivedAmount", 0))
            vuelto = max(recibido - p["totalAmount"], 0)
            lines.append(f"Recibido: ${recibido}")
            lines.append(f"Vuelto:   ${vuelto}")
        elif method == "crédito":
            lines.append("Expira: " + str(detail.get("creditExpiration", "N/A")))
            if detail.get("initialPayment"):
                lines.append("Abono: $" + str(detail["initialPayment"]))

        lines.append("")
        lines.append(center("ChamaFruit 🍌"))

        return "\n".join(lines)

        lines = []
        center = lambda t: t.center(32)
        right = lambda t: t.rjust(32)

        lines.append(center("Comprobante de Venta"))
        lines.append("-" * 32)
        lines.append(f"Nro Venta: {p['id']}")
        lines.append(f"Fecha: {p['createdAt'][:16].replace('T',' ')}")
        lines.append("")

        if p.get("Client"):
            c = p["Client"]
            lines.extend([
                f"Nombre: {c.get('name', 'N/A')}",
                f"RUT: {c.get('rut', 'N/A')}",
                f"Email: {c.get('email', 'N/A')}",
                f"Dirección: {c.get('address', 'N/A')}",
                f"Ciudad: {c.get('city', 'N/A')}",
                f"Teléfono: {c.get('phone', 'N/A')}"
            ])
        else:
            lines.append("Venta sin cliente")

        lines.append("")
        lines.append("Detalle:")
        for item in p["items"]:
            if item["quantity"] <= 0:
                continue
            name = item["varietyName"]
            qty = item["quantity"]
            price = item["price"]
            unit = item.get("metricUnit") or "u"
            total = qty * price
            lines.append(f"{name} x{qty} ({price} c/{unit})"[:28])
            lines.append(right(f"${total:,.0f}".replace(",", ".")))

        lines.append("-" * 32)
        lines.append(right(f"Total: ${p['totalAmount']:,.0f}".replace(",", ".")))
        lines.append("")

        method = p.get("paymentMethod", "No especificado")
        detail = p.get("detailForPayment") or {}

        lines.append("Método de pago: " + method)
        if method == "cheque":
            lines.append("Cheque N°: " + str(detail.get("chequeNumber", "N/A")))
            lines.append("Expira: " + str(detail.get("chequeExpiration", "N/A")))
            if detail.get("initialPayment"):
                lines.append("Abono: $" + str(detail["initialPayment"]))
        elif method in ["tarjeta", "transferencia"]:
            lines.append("Transacción: " + str(detail.get("transactionNumber", "N/A")))
        elif method == "efectivo":
            received = int(detail.get("receivedAmount", 0))
            change = max(received - p["totalAmount"], 0)
            lines.append(f"Recibido: ${received}")
            lines.append(f"Vuelto: ${change}")
        elif method == "crédito":
            lines.append("Expira: " + str(detail.get("creditExpiration", "N/A")))
            if detail.get("initialPayment"):
                lines.append("Abono: $" + str(detail["initialPayment"]))

        lines.append("")
        lines.append(center("ChamaFruit 🍌"))
        return "\n".join(lines)

    def test_width(self):
        try:
            ser = serial.Serial(self.port, baudrate=9600, timeout=1)
            time.sleep(1)
            for i in range(20, 51):
                test_line = f"{i} chars: " + "-" * (i - len(f"{i} chars: "))
                ser.write(test_line[:i].encode("ascii", errors="ignore"))
                ser.write(b'\n')
            time.sleep(0.5)
            ser.write(b'\n\n\n\x1d\x56\x41')  # Cut
            ser.close()
        except Exception as e:
            print("Test error:", e)
