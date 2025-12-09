import json

from PyQt5 import QtCore, QtGui, QtWidgets
import os
import traceback
from datetime import datetime

from Model.Flight import Flight
from QtDesigner.ScheduleFlight import addFlight
from Service.IsoCountry import IsoCountry
from Service.determine_holidays import exist_holidays
from Service.determine_tourist_attraction import classify_tourism
from Service.distance_calculation import distance_between_countries
from Service.stops_estimation import choose_aircraft, estimate_stops
from constants.Airline_Specific_Constants.Fuel_Cost import FUEL_COST_Km


def get_isocode(country):
    return IsoCountry.get(country)


def load_settings():
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            return settings
        except:
            return {}
    return {}


class FlightCalculationThread(QtCore.QThread):
    """QThread to handle flight calculations without freezing UI"""
    calculation_finished = QtCore.pyqtSignal(dict)
    calculation_error = QtCore.pyqtSignal(str)

    def __init__(self, from_country, to_country, departure_date, return_date, fuel_cost_per_km):
        super().__init__()
        self.from_country = from_country
        self.to_country = to_country
        self.departure_date = departure_date
        self.return_date = return_date
        self.fuel_cost_per_km = fuel_cost_per_km
        self.running = True

    def run(self):
        try:
            if not self.running:
                return

            # Calculate distance and aircraft
            result = choose_aircraft(self.from_country, self.to_country)

            if result is None:
                self.calculation_error.emit("No aircraft found for this route.")
                return

            distance, airplane = result

            if not self.running:
                return

            # Calculate number of stops
            stops = estimate_stops(self.from_country, self.to_country)

            if not self.running:
                return

            # Calculate fuel cost
            fuel_cost = distance * self.fuel_cost_per_km * airplane["cost_factor"]

            if not self.running:
                return

            # Check holidays
            try:
                holidays_info = exist_holidays(self.from_country, self.departure_date, self.return_date)
            except Exception as e:
                holidays_info = f"Error: {str(e)}"

            if not self.running:
                return

            # Check tourism classification
            try:
                tourism_class = classify_tourism(self.to_country)
            except Exception as e:
                tourism_class = f"Error: {str(e)}"

            if not self.running:
                return

            # Prepare result dictionary
            result_data = {
                'distance': distance,
                'airplane': airplane,
                'stops': stops,
                'fuel_cost': fuel_cost,
                'holidays': holidays_info,
                'tourism': tourism_class,
                'from_country': self.from_country,
                'to_country': self.to_country
            }

            self.calculation_finished.emit(result_data)

        except Exception as e:
            if self.running:
                self.calculation_error.emit(f"Error calculating flight details: {str(e)}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait(1000)


class Ui_FlightPlanningWindow(object):

    def __init__(self):
        super().__init__()
        self.main_window_reference = None  # Will store reference to main window
        self.calculation_thread = None
        self.calculation_in_progress = False

    def set_main_window_reference(self, main_window_ui):
        self.main_window_reference = main_window_ui

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("FlightPlanningWindow")
        MainWindow.resize(1200, 900)
        MainWindow.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f0f8ff;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        self.scrollArea = QtWidgets.QScrollArea(MainWindow)
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

        # WELCOME LABEL
        self.welcome_label = QtWidgets.QLabel("Flight Planning Interface")
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
        self.datetime_departure.setDisplayFormat("yyyy-MM-dd HH:mm")
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
        self.datetime_return.setDisplayFormat("yyyy-MM-dd HH:mm")
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
        self.group_route = QtWidgets.QGroupBox("Route Selection")
        self.group_route.setStyleSheet("""
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
        main_layout.addWidget(self.group_route)

        route_layout = QtWidgets.QHBoxLayout(self.group_route)
        route_layout.setContentsMargins(30, 30, 30, 30)
        route_layout.setSpacing(40)

        # From country
        from_layout = QtWidgets.QVBoxLayout()
        self.label_from_country = QtWidgets.QLabel("From Country:")
        self.label_from_country.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        from_layout.addWidget(self.label_from_country)

        self.combo_from = QtWidgets.QComboBox()
        self.combo_from.addItem("")  # Empty first item
        self.combo_from.addItems(sorted(IsoCountry.keys()))
        self.combo_from.setStyleSheet("""
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
        from_layout.addWidget(self.combo_from)
        route_layout.addLayout(from_layout)

        # To country
        to_layout = QtWidgets.QVBoxLayout()
        self.label_to_country = QtWidgets.QLabel("To Country:")
        self.label_to_country.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e40af;")
        to_layout.addWidget(self.label_to_country)

        self.combo_to = QtWidgets.QComboBox()
        self.combo_to.addItem("")  # Empty first item
        self.combo_to.addItems(sorted(IsoCountry.keys()))
        self.combo_to.setStyleSheet("""
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
        to_layout.addWidget(self.combo_to)
        route_layout.addLayout(to_layout)

        route_layout.addStretch()

        # FLIGHT CALCULATIONS SECTION (initially hidden)
        self.group_calculations = QtWidgets.QGroupBox("Flight Calculations")
        self.group_calculations.setStyleSheet("""
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
        self.group_calculations.setVisible(False)
        main_layout.addWidget(self.group_calculations)

        self.calculations_layout = QtWidgets.QVBoxLayout(self.group_calculations)
        self.calculations_layout.setContentsMargins(25, 30, 25, 25)
        self.calculations_layout.setSpacing(20)

        # Grid for calculation results
        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(15)

        labels = [
            "Distance:",
            "Airplane:",
            "Capacity:",
            "Number of Stops:",
            "Fuel Cost:",
            "Holidays:",
            "Tourist Destination:"
        ]

        self.vals = {}

        for i, text in enumerate(labels):
            lab = QtWidgets.QLabel(text)
            val = QtWidgets.QLabel("-")

            lab.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e40af;")
            val.setStyleSheet(
                "font-size: 18px; color: #475569; background-color: #f8fafc; padding: 8px 15px; border-radius: 8px; border: 1px solid #d1d5db;")

            grid.addWidget(lab, i, 0)
            grid.addWidget(val, i, 1)

            self.vals[text] = val

        self.calculations_layout.addLayout(grid)

        # Save Flight button
        self.save_button = QtWidgets.QPushButton("Save Flight")
        self.save_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                font-weight: bold;
                color: white;
                background-color: #10b981;
                padding: 15px 30px;
                border-radius: 12px;
                border: none;
                min-width: 250px;
                margin-top: 20px;
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
        self.save_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.saveFlight)
        self.calculations_layout.addWidget(self.save_button, 0, QtCore.Qt.AlignCenter)

        # Progress indicator
        self.progress_label = QtWidgets.QLabel("")
        self.progress_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #1e40af;
                font-style: italic;
                padding: 5px;
            }
        """)
        self.progress_label.setAlignment(QtCore.Qt.AlignCenter)
        self.calculations_layout.addWidget(self.progress_label)

        # Add stretch at the end
        main_layout.addStretch()

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        MainWindow.setCentralWidget(self.scrollArea)

        # Load settings
        self.settings = load_settings()
        print("Loaded settings:", self.settings)

        # Initialize state
        self.from_country = None
        self.to_country = None
        self.current_flight_data = None
        self.calculation_in_progress = False

        # Initialize synchronization
        self.sync_calendars()

        # Connect signals
        self.calendar_departure.selectionChanged.connect(self.sync_departure_from_calendar)
        self.datetime_departure.dateTimeChanged.connect(self.sync_departure_from_time)
        self.calendar_return.selectionChanged.connect(self.sync_return_from_calendar)
        self.datetime_return.dateTimeChanged.connect(self.sync_return_from_time)

        self.datetime_departure.dateTimeChanged.connect(self.validate_dates)
        self.datetime_return.dateTimeChanged.connect(self.validate_dates)

        self.combo_from.currentTextChanged.connect(self.on_route_changed)
        self.combo_to.currentTextChanged.connect(self.on_route_changed)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def sync_calendars(self):
        current_time = QtCore.QTime(12, 0)  # Default to noon

        # Set departure to current date
        current_date = QtCore.QDate.currentDate()
        self.calendar_departure.setSelectedDate(current_date)
        self.datetime_departure.setDateTime(QtCore.QDateTime(current_date, current_time))

        # Set return to tomorrow
        tomorrow = current_date.addDays(1)
        self.calendar_return.setSelectedDate(tomorrow)
        self.datetime_return.setDateTime(QtCore.QDateTime(tomorrow, current_time))

    def sync_departure_from_calendar(self):
        """Sync datetime editor when calendar changes"""
        selected_date = self.calendar_departure.selectedDate()
        current_time = self.datetime_departure.time()

        self.datetime_departure.blockSignals(True)
        self.datetime_departure.setDate(selected_date)
        self.datetime_departure.setTime(current_time)
        self.datetime_departure.blockSignals(False)

        if self.datetime_return.dateTime() <= self.datetime_departure.dateTime():
            return_date = selected_date.addDays(1)
            self.calendar_return.setSelectedDate(return_date)
            self.datetime_return.blockSignals(True)
            self.datetime_return.setDate(return_date)
            self.datetime_return.setTime(current_time)
            self.datetime_return.blockSignals(False)

    def sync_departure_from_time(self):
        """Sync calendar when time changes"""
        current_datetime = self.datetime_departure.dateTime()
        self.calendar_departure.blockSignals(True)
        self.calendar_departure.setSelectedDate(current_datetime.date())
        self.calendar_departure.blockSignals(False)
        self.validate_dates()

    def sync_return_from_calendar(self):
        """Sync datetime editor when return calendar changes"""
        selected_date = self.calendar_return.selectedDate()
        current_time = self.datetime_return.time()

        self.datetime_return.blockSignals(True)
        self.datetime_return.setDate(selected_date)
        self.datetime_return.setTime(current_time)
        self.datetime_return.blockSignals(False)
        self.validate_dates()

    def sync_return_from_time(self):
        """Sync return calendar when time changes"""
        current_datetime = self.datetime_return.dateTime()
        self.calendar_return.blockSignals(True)
        self.calendar_return.setSelectedDate(current_datetime.date())
        self.calendar_return.blockSignals(False)
        self.validate_dates()

    def validate_dates(self):
        """Validate that return date is after departure date"""
        departure = self.datetime_departure.dateTime()
        return_date = self.datetime_return.dateTime()

        if return_date <= departure:
            self.Time_Edit_Error.setText("Return date must be after departure date!")
        else:
            self.Time_Edit_Error.setText("")

    def on_route_changed(self):
        try:
            # Get current values
            from_country = self.combo_from.currentText() or None
            to_country = self.combo_to.currentText() or None

            # Update instance variables
            self.from_country = from_country
            self.to_country = to_country

            # Stop any ongoing calculation
            if self.calculation_thread and self.calculation_thread.isRunning():
                self.calculation_thread.stop()
                self.calculation_thread.wait(500)
                self.calculation_in_progress = False

            # Only proceed if both countries are selected
            if from_country and to_country:
                if from_country == to_country:
                    self.Time_Edit_Error.setText("Departure and destination countries cannot be the same!")
                    self.group_calculations.setVisible(False)
                    self.save_button.setEnabled(False)
                    return

                # Clear error
                self.Time_Edit_Error.setText("")

                # Start calculation in separate thread
                self.start_calculation_thread()

        except Exception as e:
            print(f"Error in on_route_changed: {e}")
            traceback.print_exc()
            self.Time_Edit_Error.setText(f"Error: {str(e)}")
            self.group_calculations.setVisible(False)
            self.save_button.setEnabled(False)

    def start_calculation_thread(self):
        """Start flight calculation in a separate thread"""
        try:
            # Get dates for calculation
            departure_date = self.datetime_departure.date().toPyDate()
            return_date = self.datetime_return.date().toPyDate()
            fuel_cost_per_km = float(self.settings.get("fuel_cost", 0.0))

            # Show calculations panel with loading indicators
            self.group_calculations.setVisible(True)
            self.progress_label.setText("Calculating flight details...")

            for key in self.vals:
                self.vals[key].setText("Calculating...")

            self.save_button.setEnabled(False)
            self.calculation_in_progress = True

            # Create and start calculation thread
            self.calculation_thread = FlightCalculationThread(
                self.from_country,
                self.to_country,
                departure_date,
                return_date,
                fuel_cost_per_km
            )

            # Connect thread signals
            self.calculation_thread.calculation_finished.connect(self.on_calculation_finished)
            self.calculation_thread.calculation_error.connect(self.on_calculation_error)
            self.calculation_thread.finished.connect(self.on_thread_finished)

            # Start the thread
            self.calculation_thread.start()

        except Exception as e:
            print(f"Error starting calculation thread: {e}")
            traceback.print_exc()
            self.Time_Edit_Error.setText(f"Error: {str(e)}")
            self.group_calculations.setVisible(False)
            self.save_button.setEnabled(False)

    def on_calculation_finished(self, result_data):
        """Handle successful calculation results"""
        try:
            # Update UI with results
            self.vals["Distance:"].setText(f"{result_data['distance']:.2f} km")
            self.vals["Airplane:"].setText(result_data['airplane']['name'])
            self.vals["Capacity:"].setText(str(result_data['airplane']['capacity']))
            self.vals["Number of Stops:"].setText(str(result_data['stops']))
            self.vals["Fuel Cost:"].setText(f"${result_data['fuel_cost']:.2f}")
            self.vals["Holidays:"].setText(str(result_data['holidays']))
            self.vals["Tourist Destination:"].setText(str(result_data['tourism']))

            # Store flight data for saving
            self.current_flight_data = {
                'distance': result_data['distance'],
                'airplane': result_data['airplane'],
                'stops': result_data['stops'],
                'fuel_cost': result_data['fuel_cost'],
                'departure_date': self.datetime_departure.date().toPyDate(),
                'return_date': self.datetime_return.date().toPyDate(),
                'from_country': result_data['from_country'],
                'to_country': result_data['to_country']
            }

            # Update progress label
            self.progress_label.setText("Calculation complete!")

            # Enable save button
            self.save_button.setEnabled(True)

            print("Flight details calculated successfully")

        except Exception as e:
            print(f"Error updating UI with results: {e}")
            traceback.print_exc()
            self.Time_Edit_Error.setText(f"Error displaying results: {str(e)}")
            self.group_calculations.setVisible(False)
            self.save_button.setEnabled(False)

    def on_calculation_error(self, error_message):
        """Handle calculation errors"""
        print(f"Calculation error: {error_message}")
        self.Time_Edit_Error.setText(error_message)
        self.group_calculations.setVisible(False)
        self.save_button.setEnabled(False)
        self.progress_label.setText("")

    def on_thread_finished(self):
        """Clean up after thread finishes"""
        self.calculation_in_progress = False
        if hasattr(self, 'calculation_thread'):
            self.calculation_thread.deleteLater()

    def saveFlight(self):
        try:
            if not self.current_flight_data:
                QtWidgets.QMessageBox.warning(None, "Error",
                                              "No flight data to save. Please select a route first.")
                return

            # Get dates in the correct format
            departure_date = self.datetime_departure.date().toPyDate()
            return_date = self.datetime_return.date().toPyDate()

            # Format dates as strings in 'YYYY-MM-DD' format
            departure_str = departure_date.strftime('%Y-%m-%d')
            return_str = return_date.strftime('%Y-%m-%d')

            print(f"Creating flight with dates: {departure_str} to {return_str}")
            print(f"From: {self.from_country}, To: {self.to_country}")

            # Create Flight object
            try:
                # First try with string format
                flight = Flight(departure_str, return_str, self.from_country, self.to_country)
            except Exception as e1:
                print(f"First attempt failed: {e1}")
                # Try with datetime objects
                flight = Flight(departure_date, return_date, self.from_country, self.to_country)

            # Add additional flight details
            try:
                flight.distance = self.current_flight_data['distance']
                flight.aircraft = self.current_flight_data['airplane']['name']
                flight.stops = self.current_flight_data['stops']
                flight.fuel_cost = self.current_flight_data['fuel_cost']
            except AttributeError:
                # If Flight object doesn't have these attributes, that's OK
                pass

            # Save the flight
            result = addFlight(flight)
            print(f"addFlight result: {result}")

            # Trigger takeoff animation in main window if reference exists
            if self.main_window_reference:
                self.main_window_reference.triggerTakeoff()

            # AUTO-OPEN SCHEDULEFLIGHT WINDOW AFTER SAVING
            self.openScheduleFlightWindow()

            # Show confirmation message
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setWindowTitle("Flight Saved")
            msg.setText("Flight has been saved successfully!")

            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            print(flight.to_string())
            print("Flight saved successfully and takeoff animation triggered!")

        except Exception as e:
            print(f"Error saving flight: {e}")
            traceback.print_exc()

            error_msg = f"Failed to save flight: {str(e)}\n\n"
            error_msg += f"Departure date: {departure_date}\n"
            error_msg += f"Return date: {return_date}"

            QtWidgets.QMessageBox.critical(None, "Error", error_msg)

    def openScheduleFlightWindow(self):
        """Open the ScheduleFlight window after saving flight"""
        try:
            print("Opening ScheduleFlight window...")

            # Import and create ScheduleFlight window
            from QtDesigner.ScheduleFlight import Ui_Form

            # Create the window
            self.schedule_window = QtWidgets.QWidget()
            self.schedule_ui = Ui_Form()
            self.schedule_ui.setupUi(self.schedule_window)

            # Show the window
            self.schedule_window.show()
            self.schedule_window.raise_()  # Bring to front

            print("ScheduleFlight window opened!")

        except ImportError as e:
            print(f"Error importing ScheduleFlight: {e}")
            QtWidgets.QMessageBox.critical(
                None,
                "Error",
                f"Cannot open ScheduleFlight window:\n{str(e)}"
            )
        except Exception as e:
            print(f"Error opening ScheduleFlight: {e}")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Flight Planning"))

    def planflight(self, main_window_ui=None):
        """Launch flight planning window with optional reference to main window"""
        import sys
        app = QtWidgets.QApplication(sys.argv)
        app.setStyle("Fusion")

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(240, 248, 255))
        palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(30, 64, 175))
        app.setPalette(palette)

        MainWindow = QtWidgets.QMainWindow()
        ui = Ui_FlightPlanningWindow()

        # Set reference to main window if provided
        if main_window_ui:
            ui.set_main_window_reference(main_window_ui)

        ui.setupUi(MainWindow)
        MainWindow.show()
        sys.exit(app.exec_())