import datetime
import time
import sys
from PySide2.QtWidgets import QPushButton, QApplication, QVBoxLayout, QDialog, QTextEdit
from PySide2.QtGui import QTextCharFormat, QTextCursor, QBrush
from PyQt5.QtCore import QTimer, Qt

"""
display set text
start timer
prompt_input
end timer
check if correct
calculate time diff
return results (time diff, word count)
"""


class Form(QDialog):
    def __init__(self, samp_text, parent=None):
        super(Form, self).__init__(parent)
        self.start_time = 0
        self.end_time = 0

        self.setWindowTitle("Typing racer")

        # widgets
        self.sample_text = QTextEdit(samp_text)

        self.edit_cursor2 = QTextCursor()
        self.highlight_format2 = QTextCharFormat()
        self.highlight_brush2 = QBrush()
        self.highlight_color2 = Qt.red
        self.highlight_brush2.setColor(self.highlight_color2)
        self.highlight_format2.setBackground(self.highlight_brush2)
        #
        self.edit_cursor2.setCharFormat(self.highlight_format2)
        # self.sample_text.setTextCursor(self.edit_cursor2)
        # self.edit_cursor2.setPosition(3)
        # self.edit_cursor2.setPosition(7, QTextCursor.KeepAnchor)

        self.sample_text.setReadOnly(True)
        self.sample_text.setDisabled(True)

        self.edit = QTextEdit()
        self.edit.setDisabled(True)

        # Cursor and it's format
        self.edit_cursor = QTextCursor()
        self.highlight_format = QTextCharFormat()
        self.edit_cursor.setCharFormat(self.highlight_format)
        self.highlight_brush = QBrush()
        self.highlight_color = Qt.red
        # self.highlight_color.red()
        self.highlight_brush.setColor(self.highlight_color)
        self.highlight_format.setBackground(self.highlight_brush)

        self.button_sub = QPushButton("Submit")
        self.button_sub.setDisabled(True)

        self.button_st = QPushButton("Start", self)
        self.button_st.setUpdatesEnabled(True)

        # Qt specific tools
        self.timer_qt = QTimer()
        self.timer_qt.setInterval(1000)
        self.timer_qt.setSingleShot(True)

        # self.type_timer = QTimer()

        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button_st)
        layout.addWidget(self.sample_text)
        layout.addWidget(self.edit)
        layout.addWidget(self.button_sub)

        # Set dialog layout
        self.setLayout(layout)

        # Add button signal to greetings slot
        self.button_st.clicked.connect(self.start)
        self.button_sub.clicked.connect(self.submit)

        # Add text change signal for
        self.edit.textChanged.connect(self.check_text_with_change)

    # Submits the result
    def submit(self):
        self.end_time = datetime.datetime.now()

    def start(self):
        for sec in counter(1):
            self.button_st.setText(f'Starting in {sec}...')

        # conditional state change
        self.button_st.setDisabled(True)
        self.button_sub.setDisabled(False)
        self.edit.setDisabled(False)
        # start timer before focus is set on field (might avoid slight miliseconds error)
        self.start_time = datetime.datetime.now()
        self.edit.setFocus()

    def check_text_with_change(self):
        input_text = self.edit.toPlainText()
        for letter_num, symbol in enumerate(input_text):
            if symbol != text_sample[letter_num]:

                # self.edit_cursor.setPosition(letter_num)
                # self.edit_cursor.setPosition(len(input_text) - 1, QTextCursor.KeepAnchor)
                # self.sample_text.setTextCursor(self.edit_cursor2)

                return
        if input_text == text_sample:
            self.end_time = self.end_time = datetime.datetime.now()


def counter(time_wait):
    for sec in range(time_wait + 1):
        yield time_wait - sec
        time.sleep(1)


text_sample = ('There are only two ways to live your life. One is as though nothing is a miracle.'
               ' The other is as though everything is a miracle.')

if __name__ == '__main__':
    # Create the Qt Application
    app = QApplication(sys.argv)

    # Create and show the form
    form = Form(text_sample)
    form.show()

    # Run the main Qt loop
    sys.exit(app.exec_())
