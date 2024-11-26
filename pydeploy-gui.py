import sys
import pydeploy

from PySide6.QtWidgets import *
from PySide6 import QtCore, QtGui

class PyDeployGui(QWidget):
    def __init__(self):
        super().__init__()

        # Declare widgets in their groups
        self.create_nav_buttons()
        self.create_form_group_box()

        # Add Widgets
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self._form_group_box)
        self.layout.addWidget(self._horizontal_group_box)

        # Declare button functionality
        self.deploy_button.clicked.connect(self.exit)
        self.cancel_button.clicked.connect(self.exit)

    def create_nav_buttons(self) -> None:
        self._horizontal_group_box = QGroupBox()  # Can put a title here
        layout = QHBoxLayout()

        # Create Buttons
        self.deploy_button = QPushButton("Deploy")
        self.cancel_button = QPushButton("Cancel")

        # Add Buttons
        layout.addWidget(self.deploy_button)
        layout.addWidget(self.cancel_button)

        # Save the layout
        self._horizontal_group_box.setLayout(layout)

    def create_form_group_box(self) -> None:
        # Create Layout
        self._form_group_box = QGroupBox("Patch Selection")
        layout = QFormLayout()

        self.csv_file = QLineEdit()  # Place holder until I find the proper widget
        self.csv_column = QLineEdit()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.parameter_input = QLineEdit()
        self.patch_box = QComboBox()

        # Add Rows to the Form
        layout.addRow(QLabel("Username:"), self.username_input)
        layout.addRow(QLabel("Password:"), self.password_input)
        layout.addRow(QLabel("Computer CSV:"), self.csv_file)
        layout.addRow(QLabel("CSV Column:"), self.csv_column)
        layout.addRow(QLabel("Patch:"), self.patch_box)
        layout.addRow(QLabel("Extra Parameters:"), self.parameter_input)

        self.patch_box.addItems(pydeploy.read_patches())

        # Save the layout
        self._form_group_box.setLayout(layout)

    def deploy(self) -> None:
        """Function for pushing the deployment"""
        # TODO: Make the extra parameters do stuff
        computers = pydeploy.get_computers(self.csv_file.text, self.csv_column.text)

        pydeploy.deploy_software(self.username_input.text, self.password_input.text, self.patch_box.itemText, computers, self.parameter_input.text)

        # TODO: Popup showing the systems it succeeded on and the systems it failed on

    def exit(self) -> None:
        """Silly little funciton to quit the program"""
        exit()

if __name__ == "__main__":
    app = QApplication([])

    # TODO: Maybe make everything in the other file a class...
    pydeploy.health_check()

    widget = PyDeployGui()
    #widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())