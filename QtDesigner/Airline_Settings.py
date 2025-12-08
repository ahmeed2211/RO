# -*- coding: utf-8 -*-
import sys
import json
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from constants.Airline_Specific_Constants import Seat_Types
from constants.Airline_Specific_Constants.Base_Seat_Cost import BASE_SEAT_PRICE
from constants.Airline_Specific_Constants.Fuel_Cost import FUEL_COST_Km
from constants.Airline_Specific_Constants.Luggage_cost import LUGGAGE_COST_PER_KG
from QtDesigner.PlanFlight import Ui_FlightPlanningWindow as PlanFlightUI


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airline Management System - Settings")
        self.resize(1850, 1000)
        self.setMinimumSize(1400, 800)
        self.showMaximized()

        self.special_count = 0
        self.saved = False

        self.setup_ui()
        self.load_settings()

    def setup_ui(self):

        self.setStyleSheet(f"""
            QMainWindow {{
                background-image: url("C:/GL3/Sem1/RO/background_image2.jpg");
                background-repeat: no-repeat;
                background-position: center;
                background-attachment: fixed;
            }}

            /* translucent overlay so text stays readable */
            QWidget#overlay {{
                background: rgba(255,255,255,0.55);
                border-radius: 20px;
            }}

            QLabel {{
                font-size:26px;
                font-weight:600;
                color:#1e40af;
            }}
            QLabel#header {{
                font-size:60px;
                font-weight:bold;
                margin:20px;
            }}
            QLabel#section {{
                font-size:40px;
                font-weight:bold;
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                                          stop:0 #dbeafe, stop:1 #bfdbfe);
                padding:20px; border-radius:20px; margin:30px 0 20px;
            }}

            QLineEdit {{
                padding:20px;
                border:3px solid #94a3b8;
                border-radius:16px;
                font-size:24px;
                background:white;
            }}

            QPushButton {{
                background:#3b82f6;
                color:white;
                font-weight:bold;
                padding:20px;
                border-radius:16px;
                font-size:24px;
            }}
            QPushButton:hover {{ background:#2563eb; }}
            QPushButton#addBtn {{
                background:#ec4899;
                font-size:26px;
                min-height:80px;
            }}
            QPushButton#loadBtn {{
                background:#8b5cf6;
                font-size:24px;
            }}
        """)

        central = QtWidgets.QWidget()
        central.setObjectName("overlay")  # overlay ON
        self.setCentralWidget(central)

        main_layout = QtWidgets.QVBoxLayout(central)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # TOP BUTTONS LAYOUT
        top_buttons_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(top_buttons_layout)

        # LOAD DEFAULT BUTTON
        self.load_default_btn = QtWidgets.QPushButton("📥 Load Default Values")
        self.load_default_btn.setObjectName("loadBtn")
        self.load_default_btn.clicked.connect(self.load_default_values)
        top_buttons_layout.addWidget(self.load_default_btn)

        # LOAD FROM FILE BUTTON
        self.load_file_btn = QtWidgets.QPushButton("📁 Load from JSON File")
        self.load_file_btn.setObjectName("loadBtn")
        self.load_file_btn.clicked.connect(self.load_from_file)
        top_buttons_layout.addWidget(self.load_file_btn)

        top_buttons_layout.addStretch()

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        main_layout.addWidget(scroll)

        container = QtWidgets.QWidget()
        scroll.setWidget(container)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setAlignment(QtCore.Qt.AlignTop)

        header = QtWidgets.QLabel("SkyHigh Airlines")
        header.setObjectName("header")
        header.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(header)

        form_widget = QtWidgets.QWidget()
        form_widget.setMinimumWidth(1500)
        layout.addWidget(form_widget, alignment=QtCore.Qt.AlignCenter)

        self.form_layout = QtWidgets.QFormLayout(form_widget)
        self.form_layout.setVerticalSpacing(30)

        r = 0

        self.add_row("Airline Efficiency :", "efficiency", "efficiency", r);
        r += 1
        self.add_row("Base Ticket Price :", "base_price", "base_price", r);
        r += 1
        self.add_row("Fuel Cost ($/km) :", "fuel_cost", "fuel_cost", r);
        r += 1

        self.add_section("Additional Charges", r);
        r += 1
        for t, n, a in [
            ("Weekend Booking Surcharge (%) :", "weekend_surcharge", "weekend_surcharge"),
            ("Late Booking Surcharge (%) :", "late_booking", "late_booking"),
            ("Holidays Factor (%) :", "holiday_factor", "holiday_factor"),
            ("Luggage Surcharge ($/KG) :", "luggage_surcharge", "luggage_surcharge"),
            ("Tourist Destination Surcharge (%) :", "tourist_surcharge", "tourist_surcharge")
        ]:
            self.add_row(t, n, a, r);
            r += 1

        self.add_section("Seat Types", r);
        r += 1
        self.form_layout.setWidget(r, QtWidgets.QFormLayout.LabelRole,
                                   QtWidgets.QLabel("<b>Seat Type</b>"))
        self.form_layout.setWidget(r, QtWidgets.QFormLayout.FieldRole,
                                   QtWidgets.QLabel("<b>Cost Factor</b>"))
        r += 1
        for t, n, a in [
            ("Economic :", "economy_factor", "economy_factor"),
            ("Premium Economy :", "premium_economy_factor", "premium_economy_factor"),
            ("Business :", "business_factor", "business_factor"),
            ("First Class :", "first_class_factor", "first_class_factor")
        ]:
            self.add_row(t, n, a, r);
            r += 1

        self.add_section("Discounts", r);
        r += 1
        self.add_row("Advanced Booking Discount (%) :", "advanced_booking_discount", "advanced_booking_discount", r);
        r += 1
        self.add_row("Two-ways Discount (%) :", "roundtrip_discount", "roundtrip_discount", r);
        r += 1
        self.add_row("Stop Discount (%) :", "stop_discount", "stop_discount", r);
        r += 1

        self.add_section("Special Offers", r);
        r += 1
        self.special_insert_row = r
        self.add_special("Student :", "student_discount", "student_discount")

        self.add_button = QtWidgets.QPushButton("Add Another Special Offer")
        self.add_button.setObjectName("addBtn")
        self.add_button.clicked.connect(self.add_new_special)
        self.form_layout.addRow(self.add_button)

        self.add_section("Aircraft Types", self.form_layout.rowCount())
        for t, n, a in [
            ("Narrow Cost Factor :", "narrow_cost_factor", "narrow_cost_factor"),
            ("Extended Cost Factor :", "extended_cost_factor", "extended_cost_factor"),
            ("Long Cost Factor :", "long_cost_factor", "long_cost_factor"),
            ("Ultra Cost Factor :", "ultra_cost_factor", "ultra_cost_factor")
        ]:
            self.add_row(t, n, a, self.form_layout.rowCount())

        # SAVE BUTTON
        save_btn = QtWidgets.QPushButton("💾 SAVE CHANGES")
        save_btn.setStyleSheet("background:#22c55e; font-size:24px; padding:25px;")
        save_btn.clicked.connect(self.save_changes)
        self.form_layout.addRow(save_btn)

        # PLAN FLIGHT BUTTON
        big = QtWidgets.QPushButton("✈️ PLAN A FLIGHT")
        big.setStyleSheet("background:#f59e0b; font-size:28px; padding:30px;")
        big.clicked.connect(self.plan_flight)
        self.form_layout.addRow(big)

        layout.addStretch()

    # ----------------------------------------------------------
    def add_row(self, label, field_name, attr, row):
        """Add a row with label and text field"""
        lbl = QtWidgets.QLabel(label)
        edit = QtWidgets.QLineEdit()
        setattr(self, attr, edit)
        edit.field_name = field_name  # Store JSON field name
        self.form_layout.setWidget(row, QtWidgets.QFormLayout.LabelRole, lbl)
        self.form_layout.setWidget(row, QtWidgets.QFormLayout.FieldRole, edit)

    # ----------------------------------------------------------
    def add_special(self, label, field_name, attr):
        """Add a special offer row"""
        row = self.form_layout.rowCount()
        lbl = QtWidgets.QLabel(label)
        lbl.setStyleSheet("color:#7c3aed; font-weight:bold; font-size:26px;")
        edit = QtWidgets.QLineEdit()
        edit.setPlaceholderText("e.g. 15%")
        setattr(self, attr, edit)
        edit.field_name = field_name

        # Store special offer info
        edit.special_index = self.special_count

        self.form_layout.insertRow(row, lbl, edit)
        self.special_count += 1
        self.special_insert_row = row + 1

    # ----------------------------------------------------------
    def add_section(self, text, row):
        sec = QtWidgets.QLabel(text)
        sec.setObjectName("section")
        sec.setAlignment(QtCore.Qt.AlignCenter)
        self.form_layout.setWidget(row, QtWidgets.QFormLayout.SpanningRole, sec)

    def add_new_special(self):
        row = self.special_insert_row

        name_lbl = QtWidgets.QLabel("Offer Name :")
        name_edit = QtWidgets.QLineEdit()
        name_edit.setPlaceholderText("e.g., Senior Citizen, Family, etc.")
        val_lbl = QtWidgets.QLabel("Offer Value :")
        val_edit = QtWidgets.QLineEdit()
        val_edit.setPlaceholderText("e.g. 20% or 50$")

        self.form_layout.insertRow(row, name_lbl, name_edit)
        self.form_layout.insertRow(row + 1, val_lbl, val_edit)

        # Store references
        setattr(self, f"special_name_{self.special_count}", name_edit)
        setattr(self, f"special_value_{self.special_count}", val_edit)

        # Mark as special
        name_edit.is_special_name = True
        name_edit.special_index = self.special_count
        val_edit.is_special_value = True
        val_edit.special_index = self.special_count

        self.special_count += 1
        self.special_insert_row = row + 2
        self.saved = False

        QtCore.QTimer.singleShot(50, self.scroll_to_bottom)

    # ----------------------------------------------------------
    def scroll_to_bottom(self):
        scroll = self.centralWidget().findChild(QtWidgets.QScrollArea)
        sb = scroll.verticalScrollBar()
        sb.setValue(sb.maximum())

    # ----------------------------------------------------------
    def load_settings(self):
        if os.path.exists("settings.json"):
            self.load_from_file()
        else:
            self.load_default_values()

    # ----------------------------------------------------------
    def load_default_values(self):
        DEFAULT_VALUES = {
            "efficiency": "0.85",
            "base_price": str(BASE_SEAT_PRICE),
            "fuel_cost": str(FUEL_COST_Km),

            "weekend_surcharge": "0.10",
            "late_booking": "0.15",
            "holiday_factor": "0.20",
            "luggage_surcharge": str(LUGGAGE_COST_PER_KG),
            "tourist_surcharge": "0.12",

            "economy_factor": str(Seat_Types["Economy"]),
            "premium_economy_factor": str(Seat_Types["Premium Economy"]),
            "business_factor": str(Seat_Types["Business"]),
            "first_class_factor": str(Seat_Types["First Class"]),

            "advanced_booking_discount": "0.20",
            "roundtrip_discount": "0.10",
            "stop_discount": "0.05",

            "narrow_cost_factor": "1.0",
            "extended_cost_factor": "1.2",
            "long_cost_factor": "1.5",
            "ultra_cost_factor": "2.0",

            "special_offers": [
                {"name": "Student", "value": "15%"}
            ]
        }

        self.apply_values_to_form(DEFAULT_VALUES)
        QMessageBox.information(self, "Default Values Loaded",
                                "Default values have been loaded into the form.")

    # ----------------------------------------------------------
    def load_from_file(self):
        try:
            if not os.path.exists("settings.json"):
                QMessageBox.warning(self, "File Not Found",
                                    "settings.json not found. Loading default values.")
                self.load_default_values()
                return

            with open("settings.json", "r") as f:
                data = json.load(f)

            self.apply_values_to_form(data)


        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error",
                                "settings.json contains invalid JSON. Loading defaults.")
            self.load_default_values()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load settings: {str(e)}")

    # ----------------------------------------------------------
    def apply_values_to_form(self, data):
        # Clear existing special offers
        self.clear_special_offers()

        # Apply regular fields
        for attr_name, field in self.__dict__.items():
            if isinstance(field, QtWidgets.QLineEdit) and hasattr(field, 'field_name'):
                field_name = field.field_name
                if field_name in data:
                    field.setText(str(data[field_name]))

        # Apply special offers
        if "special_offers" in data:
            for i, offer in enumerate(data["special_offers"]):
                if i == 0:
                    # First special offer uses the predefined field
                    if hasattr(self, "student_discount"):
                        self.student_discount.setText(str(offer["value"]))
                else:
                    # Add new rows for additional offers
                    if i == 1:
                        # Clear the first special row if it's being replaced
                        self.clear_special_offers(keep_first=False)

                    # Add new special offer row
                    row = self.special_insert_row

                    name_lbl = QtWidgets.QLabel(f"{offer['name']} :")
                    name_edit = QtWidgets.QLineEdit()
                    name_edit.setText(offer["name"])
                    val_lbl = QtWidgets.QLabel("Value :")
                    val_edit = QtWidgets.QLineEdit()
                    val_edit.setText(str(offer["value"]))

                    self.form_layout.insertRow(row, name_lbl, name_edit)
                    self.form_layout.insertRow(row + 1, val_lbl, val_edit)

                    setattr(self, f"special_name_{self.special_count}", name_edit)
                    setattr(self, f"special_value_{self.special_count}", val_edit)

                    name_edit.is_special_name = True
                    name_edit.special_index = self.special_count
                    val_edit.is_special_value = True
                    val_edit.special_index = self.special_count

                    self.special_count += 1
                    self.special_insert_row = row + 2

        self.saved = False

    # ----------------------------------------------------------
    def clear_special_offers(self, keep_first=True):
        # Remove dynamically added special offers
        rows_to_remove = []

        for i in range(self.form_layout.rowCount()):
            item = self.form_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole)
            if item and item.widget():
                widget = item.widget()
                if hasattr(widget, 'is_special_name') and widget.is_special_name:
                    rows_to_remove.append(i)
                    rows_to_remove.append(i + 1)  # Remove value row too

        # Remove from bottom to top to avoid index issues
        for row in sorted(rows_to_remove, reverse=True):
            # Remove label
            label_item = self.form_layout.itemAt(row, QtWidgets.QFormLayout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().deleteLater()

            # Remove field
            field_item = self.form_layout.itemAt(row, QtWidgets.QFormLayout.FieldRole)
            if field_item and field_item.widget():
                field_item.widget().deleteLater()

            self.form_layout.removeRow(row)

        # Reset special count
        if keep_first:
            self.special_count = 1
            self.special_insert_row = self.find_special_insert_row()
        else:
            self.special_count = 0
            self.special_insert_row = self.find_special_insert_row()

    # ----------------------------------------------------------
    def find_special_insert_row(self):
        # Look for the "Add Another Special Offer" button
        for i in range(self.form_layout.rowCount()):
            item = self.form_layout.itemAt(i, QtWidgets.QFormLayout.FieldRole)
            if item and item.widget() == self.add_button:
                return i
        return self.form_layout.rowCount()

    # ----------------------------------------------------------
    def save_changes(self):
        """Save all form values to JSON file"""
        data = {}

        # Collect all regular fields
        for attr_name, field in self.__dict__.items():
            if isinstance(field, QtWidgets.QLineEdit) and hasattr(field, 'field_name'):
                field_name = field.field_name
                data[field_name] = field.text()

        # Collect special offers
        special_offers = []

        # First special offer (Student)
        if hasattr(self, "student_discount") and self.student_discount.text():
            special_offers.append({
                "name": "Student",
                "value": self.student_discount.text()
            })

        # Additional special offers
        for i in range(1, self.special_count):
            name_attr = f"special_name_{i}"
            value_attr = f"special_value_{i}"

            if hasattr(self, name_attr) and hasattr(self, value_attr):
                name_field = getattr(self, name_attr)
                value_field = getattr(self, value_attr)

                if name_field and value_field and name_field.text() and value_field.text():
                    special_offers.append({
                        "name": name_field.text(),
                        "value": value_field.text()
                    })

        data["special_offers"] = special_offers

        # Save to file
        try:
            with open("settings.json", "w") as f:
                json.dump(data, f, indent=4, sort_keys=True)

            self.saved = True
            QMessageBox.information(self, "Saved",
                                    f"✅ All changes saved to settings.json\n\n"
                                    f"Total fields saved: {len(data)}\n"
                                    f"Special offers: {len(special_offers)}")

        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save settings: {str(e)}")

    # ----------------------------------------------------------
    def plan_flight(self):
        self.flight_window = QtWidgets.QMainWindow()
        self.flight_ui = PlanFlightUI()
        self.flight_ui.setupUi(self.flight_window)
        self.flight_window.show()


# --------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())