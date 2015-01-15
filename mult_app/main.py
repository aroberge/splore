# -*- coding: utf-8 -*-
"""
Multiplication app
"""
from __future__ import print_function

import sys
from PyQt4 import Qt, QtCore, QtGui
from PyQt4.QtCore import pyqtSlot
from random import randrange


class ComputerLogic:
    def __init__(self):
        self.personal_score = 0
        self.attempts = 0
        self.gui = ComputerWindow(self)
        self.new_operation()
        self.gui.run()

    def reset_values(self):
        self.personal_score = 0
        self.attempts = 0
        self.gui.update_score('0/0')

    def new_operation(self):
        first_number = randrange(10)
        second_number = randrange(10)
        operation = str(first_number) + 'x' + str(second_number)
        self.operand_result = first_number*second_number
        self.gui.update_question(operation)
        self.gui.update_score(str(self.personal_score) + '/' + str(self.attempts))

    def analyze_answer(self, answer):
        if answer == '':
            self.gui.handle_missing_answer()
        else:
            try:
                answer = int(answer)
                self.gui.update_result('You said ' + str(answer) +
                                    ', result was ' + str(self.operand_result))
                success = int(answer) == int(self.operand_result)
                if success:
                    self.personal_score += 1
                self.gui.update_image(success)
            except ValueError:
                self.gui.update_result('Hum... Why not try with numbers ?')

            self.attempts += 1


class ComputerWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        self.parent = parent
        self.create_layout()

    def create_layout(self):
        self.setWindowTitle(u"Fais fonctionner tes méninges !")
        self.setMinimumSize(640, 400)

        layout = QtGui.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        # Create main zone, with start button and count zone
        menu = QtGui.QHBoxLayout()
        # Create the question line with label and line edit
        question_line = QtGui.QHBoxLayout()
        question_line.setMargin(0)
        # Create right button
        button_box = QtGui.QHBoxLayout()
        button_box.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        button_box.setAlignment(QtCore.Qt.AlignRight)
        # Create box for displaying result logic
        results = QtGui.QHBoxLayout()
        results.setAlignment(QtCore.Qt.AlignCenter)
        # Create box for image
        image = Qt.QHBoxLayout()
        image.setAlignment(QtCore.Qt.AlignCenter)
        # Create box for "one more" button
        retry = Qt.QHBoxLayout()
        retry.setAlignment(QtCore.Qt.AlignCenter)

        # Define all elements
        # Start new game button
        self.button_start = QtGui.QPushButton('Start new game')
        self.button_start.setMaximumWidth(120)
        self.button_start.value = 1
        self.button_start.clicked.connect(self.make_reset_app)
        # Score
        self.score = Qt.QLabel('')
        self.score.setAlignment(QtCore.Qt.AlignRight)
        # Line with question label and line edit for user answer
        self.question_label = QtGui.QLabel('')
        self.question_label.setMaximumWidth(50)
        self.question = QtGui.QLineEdit()
        self.question.setPlaceholderText('What about the result, huh ?')
        # Create White line to avoid content up on button hide
        fix_button_position = QtGui.QLabel('')
        fix_button_position.setMinimumHeight(30)
        # Create the build button with its caption
        self.build_button = QtGui.QPushButton('Verify !')
        self.build_button.setMaximumWidth(100)
        self.build_button.clicked.connect(self.show_result)
        # Create the area for displaying results, hidden by default
        self.result = QtGui.QLabel('')
        self.result.hide()
        # Display congrats or retry image, hidden by default
        self.result_image = QtGui.QLabel('')
        self.result_image.hide()
        # Add next button, hidden by default
        self.button_retry = QtGui.QPushButton('Next operation !')
        self.button_retry.value = 0
        self.button_retry.clicked.connect(self.make_reset_app)
        self.button_retry.hide()

        # Add all widgets
        menu.addWidget(self.button_start)
        menu.addWidget(self.score)
        question_line.addWidget(self.question_label)
        question_line.addWidget(self.question)
        button_box.addWidget(fix_button_position)
        button_box.addWidget(self.build_button)
        results.addWidget(self.result)
        image.addWidget(self.result_image)
        retry.addWidget(self.button_retry)

        # Add layouts to main layout
        layout.addLayout(menu)
        layout.addLayout(question_line)
        layout.addLayout(button_box)
        layout.addLayout(results)
        layout.addLayout(image)
        layout.addLayout(retry)

        # Set the VBox layout as the window's main layout
        self.setLayout(layout)

    def show_result(self):
        ''' Apply logic and show results '''
        # Get user answer
        answer = self.question.text()
        self.parent.analyze_answer(answer)

        # In all cases, show text message
        self.result.show()

    def update_result(self, text):
        self.result.setText(text)

    def update_question(self, text):
        self.question_label.setText(text)

    def update_score(self, text):
        self.score.setText(text)

    def handle_missing_answer(self):
        self.update_result('Hum... Did you click by mistake ?')
        self.result_image.hide()
        self.button_retry.hide()

    def update_image(self, success=True):
        if success:
            image = 'well-done.png'
        else:
            image = 'hum.png'
        # Hide buttons and clear elements
        self.build_button.hide()
        # Clear and Disable QLineEdit
        self.question.clear()
        self.question.setDisabled(1)
        # Display result image and button for new question
        img = QtGui.QPixmap()
        img.load('./img/'+image)
        self.result_image.setPixmap(img.scaled(200, 200, QtCore.Qt.KeepAspectRatio))
        self.result_image.show()
        self.button_retry.show()

    @pyqtSlot()
    def make_reset_app(self):
        source = self.sender()

        if source.value == 1:
            self.parent.reset_values()

        self.question.clear()
        self.question.setDisabled(0)
        self.result.hide()
        self.result_image.hide()
        self.button_retry.hide()
        self.build_button.show()
        self.parent.new_operation()

    # TODO : connect this function to the app
    def query_exit(self):
        exit = QtGui.QMessageBox.information(self,
                                        "Quit...",
                                        "Do you really want to quit ?",
                                        "&Ok",
                                        "&Cancel",
                                        "", 0, 1)
        if exit == 0:
            qt_app.quit()

    def run(self):
        # show the layout
        self.show()
        # Run the qt application
        qt_app.exec_()
        sys.exit()


# Create an instance of the application and run it
if __name__ == "__main__":
    qt_app = Qt.QApplication(sys.argv)
    Qt.QApplication.setStyle("plastique")
    app = ComputerLogic()
