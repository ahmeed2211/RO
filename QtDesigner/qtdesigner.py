import sys
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5 import uic

# Import AIRLINES from your external file
from constants.AIRLINES import AIRLINES  # make sure this file exists

# -----------------------------
# Helper to load logo from URL
# -----------------------------
def load_logo(url: str) -> QIcon:
    try:
        response = requests.get(url)
        response.raise_for_status()
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        return QIcon(pixmap)
    except Exception as e:
        print(f"[ERROR] Could not load logo {url} → {e}")
        return QIcon()  # fallback empty icon


# -----------------------------
# Main Window
# -----------------------------
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the .ui file
        uic.loadUi("qtinterface.ui", self)

        # Connect buttons on login page
        self.btnAirline.clicked.connect(self.show_airline_dashboard)
        self.btnCustomer.clicked.connect(self.show_customer_dashboard)

        # Load airlines into a ListWidget (if you want one)
        # NOTE: Your .ui doesn't currently have a ListWidget for airlines.
        # You can create one in Qt Designer and name it `airlineListWidget`
        # self.load_airlines()

    # -----------------------------
    # Dashboard switching
    # -----------------------------
    def show_customer_dashboard(self):
        self.stackedWidget.setCurrentWidget(self.page_customer)

    def show_airline_dashboard(self):
        self.stackedWidget.setCurrentWidget(self.page_airline)

    # -----------------------------
    # Load airlines (optional)
    # -----------------------------
    def load_airlines(self):
        if not hasattr(self, "airlineListWidget"):
            print("No airlineListWidget in UI, skipping load.")
            return

        self.airlineListWidget.clear()
        for name, data in AIRLINES.items():
            icon = load_logo(data["logo"])
            item = QListWidgetItem(icon, f"{name}  |  Eff: {data['efficiency']}")
            self.airlineListWidget.addItem(item)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
