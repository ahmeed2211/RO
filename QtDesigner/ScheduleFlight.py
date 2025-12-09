from PyQt5 import QtCore, QtGui, QtWidgets
import os
import json
from datetime import datetime

from Model.Flight import Flight
from Model.SpecialOffer import SpecialOffer
from Model.Ticket import Ticket


def load_settings():
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return {}
    return {}


Available_Flights = []


def addFlight(flight):
    Available_Flights.append(flight)
    print(Available_Flights)


def getOffers():
    settings = load_settings()
    offers = []

    if "special_offers" in settings and settings["special_offers"]:
        for offer in settings["special_offers"]:
            # Create a user-friendly display text
            offer_name = offer.get("name", "Unknown Offer")
            offer_value = offer.get("value", "0")

            if "%" in str(offer_value):
                display_text = f"{offer_name} ({offer_value})"
            else:
                display_text = f"{offer_name} ({offer_value}%)"

            offer_id = offer_name.lower().replace(" ", "_")

            offers.append((display_text, offer_id))

    return offers


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1200, 900)
        Form.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f0f8ff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setGeometry(QtCore.QRect(0, 0, 1200, 900))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setStyleSheet("background-color: #f0f8ff;")

        main_layout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(25)

        self.welcome_label = QtWidgets.QLabel("Welcome to SkyHigh Airlines")
        self.welcome_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: #1e40af;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #dbeafe, stop:1 #bfdbfe);
                border-radius: 15px;
                text-align: center;
            }
        """)
        self.welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.welcome_label)

        # DATES SECTION
        self.group_dates = QtWidgets.QGroupBox("Select Travel Dates")
        self.group_dates.setStyleSheet("""
            QGroupBox {
                font-size: 22px;
                font-weight: bold;
                color: #1e40af;
                border: 3px solid #3b82f6;
                border-radius: 15px;
                padding-top: 15px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }
        """)
        main_layout.addWidget(self.group_dates)

        self.datesLayout = QtWidgets.QHBoxLayout(self.group_dates)
        self.datesLayout.setSpacing(40)
        self.datesLayout.setContentsMargins(25, 30, 25, 25)

        # Departure section
        self.layout_departure = QtWidgets.QVBoxLayout()
        self.layout_departure.setSpacing(15)

        self.label_departure = QtWidgets.QLabel("Departure Date")
        self.label_departure.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1e40af;
            }
        """)
        self.layout_departure.addWidget(self.label_departure)

        self.calendar_departure = QtWidgets.QCalendarWidget()
        self.calendar_departure.setStyleSheet("""
            QCalendarWidget {
                font-size: 14px;
                background-color: white;
                border: 2px solid #94a3b8;
                border-radius: 10px;
            }
            QCalendarWidget QToolButton {
                font-size: 16px;
                font-weight: bold;
                color: #1e40af;
            }
        """)
        self.calendar_departure.setMinimumSize(350, 250)
        self.layout_departure.addWidget(self.calendar_departure)

        self.datetime_departure = QtWidgets.QDateTimeEdit()
        self.datetime_departure.setDisplayFormat("yyyy-MM-dd")
        self.datetime_departure.setStyleSheet("""
            QDateTimeEdit {
                font-size: 18px;
                padding: 12px;
                border: 2px solid #94a3b8;
                border-radius: 10px;
                background-color: white;
            }
            QDateTimeEdit:hover {
                border-color: #3b82f6;
            }
        """)
        self.datetime_departure.setCalendarPopup(True)
        self.layout_departure.addWidget(self.datetime_departure)

        self.datesLayout.addLayout(self.layout_departure)

        # Return section
        self.layout_return = QtWidgets.QVBoxLayout()
        self.layout_return.setSpacing(15)

        self.label_return = QtWidgets.QLabel("Return Date")
        self.label_return.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #1e40af;
            }
        """)
        self.layout_return.addWidget(self.label_return)

        self.calendar_return = QtWidgets.QCalendarWidget()
        self.calendar_return.setStyleSheet("""
            QCalendarWidget {
                font-size: 14px;
                background-color: white;
                border: 2px solid #94a3b8;
                border-radius: 10px;
            }
            QCalendarWidget QToolButton {
                font-size: 16px;
                font-weight: bold;
                color: #1e40af;
            }
        """)
        self.calendar_return.setMinimumSize(350, 250)
        self.layout_return.addWidget(self.calendar_return)

        self.datetime_return = QtWidgets.QDateTimeEdit()
        self.datetime_return.setDisplayFormat("yyyy-MM-dd")
        self.datetime_return.setStyleSheet("""
            QDateTimeEdit {
                font-size: 18px;
                padding: 12px;
                border: 2px solid #94a3b8;
                border-radius: 10px;
                background-color: white;
            }
            QDateTimeEdit:hover {
                border-color: #3b82f6;
            }
        """)
        self.datetime_return.setCalendarPopup(True)
        self.layout_return.addWidget(self.datetime_return)

        self.datesLayout.addLayout(self.layout_return)

        # Error label for dates
        self.Time_Edit_Error = QtWidgets.QLabel("")
        self.Time_Edit_Error.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #dc2626;
                padding: 10px;
                background-color: rgba(254, 226, 226, 0.8);
                border-radius: 10px;
                text-align: center;
            }
        """)
        self.Time_Edit_Error.setAlignment(QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.Time_Edit_Error)

        # ROUTE SELECTION SECTION
        route_group = QtWidgets.QGroupBox("Route Selection")
        route_group.setStyleSheet("""
            QGroupBox {
                font-size: 22px;
                font-weight: bold;
                color: #1e40af;
                border: 3px solid #8b5cf6;
                border-radius: 15px;
                padding-top: 15px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }
        """)
        main_layout.addWidget(route_group)

        route_layout = QtWidgets.QHBoxLayout(route_group)
        route_layout.setContentsMargins(30, 30, 30, 30)
        route_layout.setSpacing(40)

        # From country
        from_layout = QtWidgets.QVBoxLayout()
        self.label_from_country = QtWidgets.QLabel("From Country:")
        self.label_from_country.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        from_layout.addWidget(self.label_from_country)

        self.combo_from_country = QtWidgets.QComboBox()
        self.combo_from_country.addItem("")  # Empty first item

        # ADD COUNTRIES FROM IsoCountry
        from Service.IsoCountry import IsoCountry
        self.combo_from_country.addItems(sorted(IsoCountry.keys()))

        self.combo_from_country.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 12px;
                border: 2px solid #94a3b8;
                border-radius: 10px;
                background-color: white;
                min-width: 250px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
        """)
        from_layout.addWidget(self.combo_from_country)
        route_layout.addLayout(from_layout)

        # To country
        to_layout = QtWidgets.QVBoxLayout()
        self.label_to_country = QtWidgets.QLabel("To Country:")
        self.label_to_country.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        to_layout.addWidget(self.label_to_country)

        self.combo_to_country = QtWidgets.QComboBox()
        self.combo_to_country.addItem("")  # Empty first item
        self.combo_to_country.addItems(sorted(IsoCountry.keys()))

        self.combo_to_country.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 12px;
                border: 2px solid #94a3b8;
                border-radius: 10px;
                background-color: white;
                min-width: 250px;
            }
            QComboBox:hover {
                border-color: #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
                width: 40px;
            }
        """)
        to_layout.addWidget(self.combo_to_country)
        route_layout.addLayout(to_layout)

        route_layout.addStretch()

        # SEAT SELECTION SECTION
        seat_group = QtWidgets.QGroupBox("Seat Selection & Options")
        seat_group.setStyleSheet("""
            QGroupBox {
                font-size: 22px;
                font-weight: bold;
                color: #1e40af;
                border: 3px solid #10b981;
                border-radius: 15px;
                padding-top: 15px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }
        """)
        main_layout.addWidget(seat_group)

        seat_form = QtWidgets.QFormLayout(seat_group)
        seat_form.setContentsMargins(30, 30, 30, 30)
        seat_form.setVerticalSpacing(20)
        seat_form.setHorizontalSpacing(40)

        # Seat type
        seat_label = QtWidgets.QLabel("Select Seat Type:")
        seat_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        seat_form.addRow(seat_label)

        self.seat_button_group = QtWidgets.QButtonGroup()
        self.radio_economy = QtWidgets.QRadioButton("Economy Class")
        self.radio_premium_economy = QtWidgets.QRadioButton("Premium Economy")
        self.radio_business = QtWidgets.QRadioButton("Business Class")
        self.radio_first_class = QtWidgets.QRadioButton("First Class")

        radio_style = """
            QRadioButton {
                font-size: 18px;
                padding: 12px;
                spacing: 15px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #94a3b8;
            }
            QRadioButton::indicator:checked {
                background-color: #3b82f6;
                border-color: #1e40af;
            }
        """
        self.radio_economy.setChecked(True)

        for radio in [self.radio_economy, self.radio_premium_economy,
                      self.radio_business, self.radio_first_class]:
            radio.setStyleSheet(radio_style)
            seat_form.addRow(radio)
            self.seat_button_group.addButton(radio)

        seat_form.addRow(QtWidgets.QLabel(""))

        # Luggage section
        luggage_label = QtWidgets.QLabel("Extra Luggage:")
        luggage_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        seat_form.addRow(luggage_label)

        luggage_layout = QtWidgets.QHBoxLayout()
        luggage_layout.setSpacing(30)

        self.checkbox_luggage_yes = QtWidgets.QCheckBox("Yes, I have extra luggage")
        self.checkbox_luggage_no = QtWidgets.QCheckBox("No extra luggage")

        checkbox_style = """
            QCheckBox {
                font-size: 17px;
                padding: 10px;
                spacing: 12px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #94a3b8;
                border-radius: 5px;
            }
            QCheckBox::indicator:checked {
                background-color: #10b981;
                border-color: #059669;
            }
        """
        self.checkbox_luggage_yes.setStyleSheet(checkbox_style)
        self.checkbox_luggage_no.setStyleSheet(checkbox_style)
        self.checkbox_luggage_no.setChecked(True)

        luggage_layout.addWidget(self.checkbox_luggage_yes)
        luggage_layout.addWidget(self.checkbox_luggage_no)
        seat_form.addRow(luggage_layout)

        # Connect luggage checkboxes
        self.checkbox_luggage_yes.clicked.connect(
            lambda: self.checkbox_luggage_no.setChecked(False) if self.checkbox_luggage_yes.isChecked() else None)
        self.checkbox_luggage_no.clicked.connect(
            lambda: self.checkbox_luggage_yes.setChecked(False) if self.checkbox_luggage_no.isChecked() else None)

        # Luggage weight input
        luggage_weight_layout = QtWidgets.QHBoxLayout()
        weight_label = QtWidgets.QLabel("Extra Luggage Weight (kg):")
        weight_label.setStyleSheet("font-size: 17px; font-weight: bold; color: #475569;")
        self.lineedit_luggage_weight = QtWidgets.QLineEdit()
        self.lineedit_luggage_weight.setPlaceholderText("Enter weight in kg")
        self.lineedit_luggage_weight.setStyleSheet("""
            QLineEdit {
                font-size: 17px;
                padding: 10px;
                border: 2px solid #94a3b8;
                border-radius: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
        """)
        self.lineedit_luggage_weight.setFixedWidth(200)
        self.lineedit_luggage_weight.setEnabled(False)
        luggage_weight_layout.addWidget(weight_label)
        luggage_weight_layout.addWidget(self.lineedit_luggage_weight)
        luggage_weight_layout.addStretch()
        seat_form.addRow(luggage_weight_layout)

        self.checkbox_luggage_yes.toggled.connect(self.lineedit_luggage_weight.setEnabled)

        # SPECIAL OFFERS SECTION
        offers_group = QtWidgets.QGroupBox("Special Offers")
        offers_group.setStyleSheet("""
            QGroupBox {
                font-size: 22px;
                font-weight: bold;
                color: #1e40af;
                border: 3px solid #ec4899;
                border-radius: 15px;
                padding-top: 15px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }
        """)
        main_layout.addWidget(offers_group)

        offers_layout = QtWidgets.QVBoxLayout(offers_group)
        offers_layout.setContentsMargins(25, 30, 25, 25)
        offers_layout.setSpacing(15)

        # Load offers from settings.json
        offers_list = getOffers()
        self.checkbox_special_offers = {}

        if offers_list:
            for offer_text, offer_id in offers_list:
                checkbox = QtWidgets.QCheckBox(offer_text)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        font-size: 17px;
                        padding: 8px;
                        spacing: 15px;
                    }
                    QCheckBox::indicator {
                        width: 20px;
                        height: 20px;
                        border: 2px solid #ec4899;
                        border-radius: 5px;
                    }
                    QCheckBox::indicator:checked {
                        background-color: #ec4899;
                    }
                """)
                offers_layout.addWidget(checkbox)
                self.checkbox_special_offers[offer_id] = checkbox
        else:
            # If no offers in settings, show a message
            no_offers_label = QtWidgets.QLabel("No special offers available at the moment.")
            no_offers_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #64748b;
                    font-style: italic;
                    padding: 10px;
                }
            """)
            no_offers_label.setAlignment(QtCore.Qt.AlignCenter)
            offers_layout.addWidget(no_offers_label)

        offers_layout.addStretch()

        # SEARCH BUTTON
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.button_search_flights = QtWidgets.QPushButton("Search Available Flights")
        self.button_search_flights.setStyleSheet("""
            QPushButton {
                font-size: 22px;
                font-weight: bold;
                color: white;
                background-color: #3b82f6;
                padding: 20px 40px;
                border-radius: 15px;
                border: none;
                min-width: 300px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        self.button_search_flights.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button_search_flights.clicked.connect(self.on_search_flights_clicked)
        button_layout.addWidget(self.button_search_flights)
        button_layout.addStretch()

        main_layout.addLayout(button_layout)

        # FLIGHT RESULTS SECTION
        self.results_group = QtWidgets.QGroupBox("Available Flights")
        self.results_group.setStyleSheet("""
            QGroupBox {
                font-size: 22px;
                font-weight: bold;
                color: #1e40af;
                border: 3px solid #f59e0b;
                border-radius: 15px;
                padding-top: 15px;
                margin-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 15px 0 15px;
            }
        """)
        self.results_group.setVisible(False)
        main_layout.addWidget(self.results_group)

        self.results_layout = QtWidgets.QVBoxLayout(self.results_group)
        self.results_layout.setContentsMargins(25, 30, 25, 25)
        self.results_layout.setSpacing(20)

        # Label for no results
        self.no_results_label = QtWidgets.QLabel("No flights found matching your criteria.")
        self.no_results_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #64748b;
                font-style: italic;
                padding: 15px;
                text-align: center;
            }
        """)
        self.no_results_label.setAlignment(QtCore.Qt.AlignCenter)
        self.results_layout.addWidget(self.no_results_label)
        self.no_results_label.setVisible(False)

        # Container for flight results
        self.flight_results_container = QtWidgets.QWidget()
        self.flight_results_layout = QtWidgets.QVBoxLayout(self.flight_results_container)
        self.flight_results_layout.setSpacing(15)
        self.results_layout.addWidget(self.flight_results_container)

        # BOOK FLIGHT BUTTON
        self.button_book_flight = QtWidgets.QPushButton("Book Selected Flight")
        self.button_book_flight.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #10b981;
                padding: 15px 30px;
                border-radius: 12px;
                border: none;
                min-width: 250px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94a3b8;
            }
        """)
        self.button_book_flight.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.button_book_flight.setEnabled(False)
        self.button_book_flight.clicked.connect(self.on_book_flight_clicked)
        self.button_book_flight.setVisible(False)
        self.results_layout.addWidget(self.button_book_flight, 0, QtCore.Qt.AlignCenter)

        main_layout.addStretch()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        # FIXED: Initialize without infinite recursion
        self.sync_calendars()

        # FIXED: Connect signals to prevent recursion
        self.calendar_departure.selectionChanged.connect(self.sync_departure_from_calendar)
        self.datetime_departure.dateTimeChanged.connect(self.sync_departure_from_time)
        self.calendar_return.selectionChanged.connect(self.sync_return_from_calendar)
        self.datetime_return.dateTimeChanged.connect(self.sync_return_from_time)

        # Validate dates when they change
        self.datetime_departure.dateTimeChanged.connect(self.validate_dates)
        self.datetime_return.dateTimeChanged.connect(self.validate_dates)

        # Store selected flight
        self.selected_flight = None

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def sync_calendars(self):
        """Initialize synchronization between calendars and datetime editors"""
        # Block signals during initial setup to prevent recursion
        self.calendar_departure.blockSignals(True)
        self.datetime_departure.blockSignals(True)
        self.calendar_return.blockSignals(True)
        self.datetime_return.blockSignals(True)

        current_time = QtCore.QTime.currentTime()

        # Set departure to current date/time
        current_date = QtCore.QDate.currentDate()
        self.calendar_departure.setSelectedDate(current_date)
        self.datetime_departure.setDateTime(QtCore.QDateTime(current_date, current_time))

        # Set return to tomorrow
        tomorrow = current_date.addDays(1)
        self.calendar_return.setSelectedDate(tomorrow)
        self.datetime_return.setDateTime(QtCore.QDateTime(tomorrow, current_time))

        # Unblock signals
        self.calendar_departure.blockSignals(False)
        self.datetime_departure.blockSignals(False)
        self.calendar_return.blockSignals(False)
        self.datetime_return.blockSignals(False)

    def sync_departure_from_calendar(self):
        """Sync datetime editor when calendar changes"""
        if not self.calendar_departure.signalsBlocked():
            selected_date = self.calendar_departure.selectedDate()
            current_time = self.datetime_departure.time()

            self.datetime_departure.blockSignals(True)
            self.datetime_departure.setDate(selected_date)
            self.datetime_departure.setTime(current_time)
            self.datetime_departure.blockSignals(False)

    def sync_departure_from_time(self):
        """Sync calendar when time changes"""
        if not self.datetime_departure.signalsBlocked():
            current_datetime = self.datetime_departure.dateTime()

            self.calendar_departure.blockSignals(True)
            self.calendar_departure.setSelectedDate(current_datetime.date())
            self.calendar_departure.blockSignals(False)

    def sync_return_from_calendar(self):
        """Sync datetime editor when return calendar changes"""
        if not self.calendar_return.signalsBlocked():
            selected_date = self.calendar_return.selectedDate()
            current_time = self.datetime_return.time()

            self.datetime_return.blockSignals(True)
            self.datetime_return.setDate(selected_date)
            self.datetime_return.setTime(current_time)
            self.datetime_return.blockSignals(False)

    def sync_return_from_time(self):
        """Sync return calendar when time changes"""
        if not self.datetime_return.signalsBlocked():
            current_datetime = self.datetime_return.dateTime()

            self.calendar_return.blockSignals(True)
            self.calendar_return.setSelectedDate(current_datetime.date())
            self.calendar_return.blockSignals(False)

    def validate_dates(self):
        """Validate that return date is after departure date"""
        # Don't validate if signals are blocked
        if self.datetime_departure.signalsBlocked() or self.datetime_return.signalsBlocked():
            return

        departure = self.datetime_departure.dateTime()
        return_date = self.datetime_return.dateTime()

        if return_date <= departure:
            self.Time_Edit_Error.setText("Return date must be after departure date!")
            self.button_search_flights.setEnabled(False)
            self.button_search_flights.setStyleSheet("""
                QPushButton {
                    font-size: 22px;
                    font-weight: bold;
                    color: white;
                    background-color: #94a3b8;
                    padding: 20px 40px;
                    border-radius: 15px;
                    border: none;
                    min-width: 300px;
                }
            """)
        else:
            self.Time_Edit_Error.setText("Dates are valid!")
            self.button_search_flights.setEnabled(True)
            self.button_search_flights.setStyleSheet("""
                QPushButton {
                    font-size: 22px;
                    font-weight: bold;
                    color: white;
                    background-color: #3b82f6;
                    padding: 20px 40px;
                    border-radius: 15px;
                    border: none;
                    min-width: 300px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
                QPushButton:pressed {
                    background-color: #1e40af;
                }
            """)

    def on_search_flights_clicked(self):
        """Handle search flights button click - collect all user selections"""
        # Collect dates (date only, no time)
        self.departure_date = self.datetime_departure.dateTime().date()
        self.return_date = self.datetime_return.dateTime().date()

        # Collect route information
        self.from_country = self.combo_from_country.currentText()
        self.to_country = self.combo_to_country.currentText()

        # Collect seat type
        if self.radio_economy.isChecked():
            self.seat_type = "Economy"
        elif self.radio_premium_economy.isChecked():
            self.seat_type = "Premium Economy"
        elif self.radio_business.isChecked():
            self.seat_type = "Business"
        elif self.radio_first_class.isChecked():
            self.seat_type = "First Class"
        else:
            self.seat_type = "Economy"  # Default

        # Collect luggage information
        self.has_extra_luggage = self.checkbox_luggage_yes.isChecked()
        self.luggage_weight = self.lineedit_luggage_weight.text() if self.has_extra_luggage else "0"

        # Collect selected special offers
        self.selected_offers = []
        for offer_id, checkbox in self.checkbox_special_offers.items():
            if checkbox.isChecked():
                self.selected_offers.append({
                    "id": offer_id,
                    "name": checkbox.text().split(" (")[0],
                    "checkbox": checkbox
                })

        # Validate required fields
        if not self.from_country or not self.to_country:
            self.Time_Edit_Error.setText("Please select both departure and destination countries!")
            return

        if self.from_country == self.to_country:
            self.Time_Edit_Error.setText("Departure and destination countries cannot be the same!")
            return

        # If all validations pass, proceed with search
        self.Time_Edit_Error.setText("Searching for flights...")
        self.search_available_flights()

    def search_available_flights(self):
        """Search through Available_Flights for matching flights"""
        # Clear previous results
        self.clear_flight_results()

        # Convert QDate to Python date
        departure_date_py = self.departure_date.toPyDate()
        return_date_py = self.return_date.toPyDate()

        print(f"🔍 Searching flights: {self.from_country} → {self.to_country}")
        print(f"📅 Dates: {departure_date_py} to {return_date_py}")
        print(f"📊 Total flights in database: {len(Available_Flights)}")

        matching_flights = []

        for i, flight in enumerate(Available_Flights):
            try:
                print(f"\n--- Checking Flight #{i} ---")

                # Debug: Check if flight has required attributes
                if not hasattr(flight, 'from_country') or not hasattr(flight, 'to_country'):
                    print(f"❌ Flight missing route attributes")
                    continue

                print(f"Flight route: {flight.from_country} → {flight.to_country}")

                # Check date attributes safely
                if not hasattr(flight, 'date_departure') or not hasattr(flight, 'date_return'):
                    print(f"❌ Flight missing date attributes")
                    continue

                # Extract dates with safe conversion
                flight_departure = None
                flight_return = None

                try:
                    # Try to get date_departure as date
                    dep_value = flight.date_departure
                    if hasattr(dep_value, 'date'):
                        flight_departure = dep_value.date()
                    elif hasattr(dep_value, 'toPyDate'):
                        flight_departure = dep_value.toPyDate()
                    elif isinstance(dep_value, str):
                        # Try to parse string date
                        flight_departure = datetime.strptime(dep_value, "%Y-%m-%d").date()
                    else:
                        flight_departure = dep_value

                    # Try to get date_return as date
                    ret_value = flight.date_return
                    if hasattr(ret_value, 'date'):
                        flight_return = ret_value.date()
                    elif hasattr(ret_value, 'toPyDate'):
                        flight_return = ret_value.toPyDate()
                    elif isinstance(ret_value, str):
                        # Try to parse string date
                        flight_return = datetime.strptime(ret_value, "%Y-%m-%d").date()
                    else:
                        flight_return = ret_value

                except Exception as date_error:
                    print(f"⚠️ Date conversion error: {date_error}")
                    continue

                if flight_departure is None or flight_return is None:
                    print(f"❌ Could not extract dates")
                    continue

                print(f"Flight dates: {flight_departure} to {flight_return}")

                # Check all conditions with safe comparison
                route_match = (str(flight.from_country) == str(self.from_country) and
                               str(flight.to_country) == str(self.to_country))

                departure_match = (str(flight_departure) == str(departure_date_py))
                return_match = (str(flight_return) == str(return_date_py))

                print(f"Route match: {route_match}")
                print(f"Departure match: {departure_match}")
                print(f"Return match: {return_match}")

                if route_match and departure_match and return_match:
                    print("✅ PERFECT MATCH FOUND!")
                    matching_flights.append(flight)

            except Exception as e:
                print(f"❌ Critical error checking flight {i}: {e}")
                import traceback
                traceback.print_exc()
                continue

        print(f"\n🎯 FINAL RESULT: Found {len(matching_flights)} matching flights")

        # Display results
        if matching_flights:
            self.display_flight_results(matching_flights)
        else:
            self.show_no_results()

        # Show results section
        self.results_group.setVisible(True)
        self.Time_Edit_Error.setText(f"Found {len(matching_flights)} matching flight(s).")

    def clear_flight_results(self):
        """Clear all flight results from the display"""
        try:
            # Remove all widgets from flight results layout
            while self.flight_results_layout.count():
                child = self.flight_results_layout.takeAt(0)
                if child and child.widget():
                    widget = child.widget()
                    widget.setParent(None)
                    widget.deleteLater()

            self.selected_flight = None
            self.button_book_flight.setEnabled(False)
            self.button_book_flight.setVisible(False)
            self.no_results_label.setVisible(False)
        except Exception as e:
            print(f"Error clearing results: {e}")

    def display_flight_results(self, flights):
        """Display matching flight results with safe attribute access"""
        self.no_results_label.setVisible(False)

        for i, flight in enumerate(flights):
            # Create flight card
            flight_card = QtWidgets.QFrame()
            flight_card.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #d1d5db;
                    border-radius: 10px;
                    padding: 15px;
                }
                QFrame:hover {
                    border-color: #3b82f6;
                    background-color: #f8fafc;
                }
            """)
            flight_card.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

            card_layout = QtWidgets.QVBoxLayout(flight_card)
            card_layout.setSpacing(10)

            # Flight header
            header_layout = QtWidgets.QHBoxLayout()

            # Flight route - safely access
            from_country = getattr(flight, 'from_country', 'Unknown')
            to_country = getattr(flight, 'to_country', 'Unknown')
            route_label = QtWidgets.QLabel(f"✈️ {from_country} → {to_country}")
            route_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e40af;")
            header_layout.addWidget(route_label)

            header_layout.addStretch()

            # Select button
            select_button = QtWidgets.QPushButton("Select")
            select_button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #3b82f6;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            select_button.clicked.connect(lambda checked, f=flight, b=select_button: self.select_flight(f, b))
            header_layout.addWidget(select_button)

            card_layout.addLayout(header_layout)

            # Flight details - safely access all attributes
            details_layout = QtWidgets.QGridLayout()
            details_layout.setHorizontalSpacing(20)
            details_layout.setVerticalSpacing(8)

            # Departure date
            dep_label = QtWidgets.QLabel("Departure:")
            dep_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(dep_label, 0, 0)

            dep_value = "Unknown"
            if hasattr(flight, 'date_departure'):
                try:
                    dep_date = flight.date_departure
                    if hasattr(dep_date, 'strftime'):
                        dep_value = dep_date.strftime("%Y-%m-%d")
                    elif hasattr(dep_date, '__str__'):
                        dep_value = str(dep_date)
                except:
                    dep_value = "Date error"

            dep_value_label = QtWidgets.QLabel(dep_value)
            dep_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(dep_value_label, 0, 1)

            # Return date
            ret_label = QtWidgets.QLabel("Return:")
            ret_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(ret_label, 1, 0)

            ret_value = "Unknown"
            if hasattr(flight, 'date_return'):
                try:
                    ret_date = flight.date_return
                    if hasattr(ret_date, 'strftime'):
                        ret_value = ret_date.strftime("%Y-%m-%d")
                    elif hasattr(ret_date, '__str__'):
                        ret_value = str(ret_date)
                except:
                    ret_value = "Date error"

            ret_value_label = QtWidgets.QLabel(ret_value)
            ret_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(ret_value_label, 1, 1)

            # Aircraft - safely access
            aircraft_label = QtWidgets.QLabel("Aircraft:")
            aircraft_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(aircraft_label, 0, 2)

            aircraft_value = "Unknown"
            if hasattr(flight, 'aircraft'):
                aircraft = flight.aircraft
                if isinstance(aircraft, dict) and 'name' in aircraft:
                    aircraft_value = aircraft['name']
                elif hasattr(aircraft, 'name'):
                    aircraft_value = aircraft.name
                elif hasattr(aircraft, '__str__'):
                    aircraft_value = str(aircraft)

            aircraft_value_label = QtWidgets.QLabel(aircraft_value)
            aircraft_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(aircraft_value_label, 0, 3)

            # Capacity
            capacity_label = QtWidgets.QLabel("Capacity:")
            capacity_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(capacity_label, 1, 2)

            capacity_value = "Unknown"
            if hasattr(flight, 'aircraft'):
                aircraft = flight.aircraft
                if isinstance(aircraft, dict) and 'capacity' in aircraft:
                    capacity_value = str(aircraft['capacity'])
                elif hasattr(aircraft, 'capacity'):
                    capacity_value = str(aircraft.capacity)

            capacity_value_label = QtWidgets.QLabel(capacity_value)
            capacity_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(capacity_value_label, 1, 3)

            # Stops - safely access
            stops_label = QtWidgets.QLabel("Estimated Stops:")
            stops_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(stops_label, 2, 0)

            stops_value = "Unknown"
            if hasattr(flight, 'determine_stops'):
                try:
                    stops_value = str(flight.determine_stops())
                except:
                    stops_value = "N/A"

            stops_value_label = QtWidgets.QLabel(stops_value)
            stops_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(stops_value_label, 2, 1)

            # Distance - safely access
            distance_label = QtWidgets.QLabel("Distance:")
            distance_label.setStyleSheet("font-size: 14px; color: #64748b;")
            details_layout.addWidget(distance_label, 2, 2)

            distance_value = "Unknown km"
            if hasattr(flight, 'distance'):
                try:
                    dist = flight.distance
                    if hasattr(dist, '__float__'):
                        distance_value = f"{float(dist):.2f} km"
                    else:
                        distance_value = f"{dist} km"
                except:
                    distance_value = "N/A"

            distance_value_label = QtWidgets.QLabel(distance_value)
            distance_value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #1e40af;")
            details_layout.addWidget(distance_value_label, 2, 3)

            card_layout.addLayout(details_layout)

            # Add flight card to results
            self.flight_results_layout.addWidget(flight_card)

        # Show book button
        self.button_book_flight.setVisible(True)

        # Add stretch at the end
        self.flight_results_layout.addStretch()

    def select_flight(self, flight, button):
        """Handle flight selection"""
        try:
            # Reset all select buttons
            for i in range(self.flight_results_layout.count()):
                item = self.flight_results_layout.itemAt(i)
                if item and item.widget():
                    card = item.widget()
                    # Find select button in this card
                    select_btn = card.findChild(QtWidgets.QPushButton)
                    if select_btn:
                        select_btn.setStyleSheet("""
                            QPushButton {
                                font-size: 14px;
                                font-weight: bold;
                                color: white;
                                background-color: #3b82f6;
                                padding: 8px 16px;
                                border-radius: 6px;
                                border: none;
                                min-width: 80px;
                            }
                            QPushButton:hover {
                                background-color: #2563eb;
                            }
                        """)
                        select_btn.setText("Select")

            button.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    background-color: #10b981;
                    padding: 8px 16px;
                    border-radius: 6px;
                    border: none;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            button.setText("Selected ✓")

            # Store selected flight
            self.selected_flight = flight
            self.button_book_flight.setEnabled(True)

        except Exception as e:
            print(f"Error selecting flight: {e}")

    def show_no_results(self):
        """Show message when no flights found"""
        self.no_results_label.setVisible(True)
        self.button_book_flight.setVisible(False)

    def on_book_flight_clicked(self):
        if not self.selected_flight:
            return

        try:
            # Create SpecialOffer objects from selected offers
            special_offers = []
            for offer in self.selected_offers:
                try:
                    # Create SpecialOffer object
                    special_offer = SpecialOffer(
                        name=offer['name'],
                        offer_id=offer['id']
                    )
                    special_offers.append(special_offer)
                except Exception as e:
                    print(f"Error creating SpecialOffer: {e}")

            # Create Ticket object
            try:
                # Get luggage weight
                luggage_weight = 0
                if self.has_extra_luggage:
                    try:
                        luggage_weight = float(self.luggage_weight) if self.luggage_weight else 0
                    except:
                        luggage_weight = 0

                ticket = Ticket(
                    date_reservation=datetime.now(),
                    flight=self.selected_flight,
                    seat_type=self.seat_type,
                    extra_luggage=luggage_weight,
                    specialoffers=special_offers
                )

                print(f"✅ Created ticket: {ticket}")
                print(f"   Ticket ID: {getattr(ticket, 'ticket_id', 'N/A')}")
                print(f"   Reservation date: {ticket.date_reservation}")
                print(f"   Flight: {ticket.flight.from_country} → {ticket.flight.to_country}")
                print(f"   Seat type: {ticket.seat_type}")
                print(f"   Extra luggage: {ticket.extra_luggage} kg")
                print(f"   Special offers: {len(ticket.specialoffers)}")
                print(f"   Weekend booking: {ticket.is_weekend()}")
                print(f"   Advanced booking: {ticket.is_advanced_booking()}")

            except Exception as e:
                print(f"❌ Error creating ticket: {e}")
                import traceback
                traceback.print_exc()

            # Show booking confirmation
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Flight Booking")
            msg.setText(f"Booking Confirmation")

            # Safely get flight details for display
            flight_info = f"Flight from {self.selected_flight.from_country} to {self.selected_flight.to_country}"
            if hasattr(self.selected_flight, 'date_departure'):
                dep_date = self.selected_flight.date_departure
                if hasattr(dep_date, 'strftime'):
                    dep_str = dep_date.strftime('%Y-%m-%d')
                else:
                    dep_str = str(dep_date)
            else:
                dep_str = "Unknown"

            msg.setInformativeText(
                f"You have selected:\n\n"
                f"• {flight_info}\n"
                f"• Departure: {dep_str}\n"
                f"• Seat Type: {self.seat_type}\n"
                f"• Extra Luggage: {'Yes' if self.has_extra_luggage else 'No'}\n"
                f"• Special Offers: {', '.join([offer['name'] for offer in self.selected_offers]) if self.selected_offers else 'None'}\n\n"
                f"Price : {ticket.determine_price()} \n"
                f"Ticket has been created successfully!\n"
                f"Would you like to proceed with payment?"
            )
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.Yes)

            ret = msg.exec_()

            if ret == QtWidgets.QMessageBox.Yes:
                self.Time_Edit_Error.setText("Flight booked and paid successfully!")

                # Reset selection
                self.selected_flight = None
                self.button_book_flight.setEnabled(False)

                # Clear results after booking
                self.clear_flight_results()
                self.results_group.setVisible(False)

        except Exception as e:
            print(f"❌ Error in booking process: {e}")
            import traceback
            traceback.print_exc()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "SkyHigh Airlines - Flight Booking"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 248, 255))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(30, 64, 175))
    app.setPalette(palette)

    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())