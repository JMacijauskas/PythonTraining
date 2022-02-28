import datetime
import time
import sys
from PySide2.QtWidgets import QLineEdit, QPushButton, QApplication, QVBoxLayout, QDialog, QTextEdit

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
        self.setWindowTitle("Typing racer")
        # widgets
        self.sample_text = QTextEdit(samp_text)
        self.sample_text.setReadOnly(True)
        self.edit = QLineEdit()
        self.button_sub = QPushButton("Submit")
        self.button_st = QPushButton("Start")
        # Create layout and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.button_st)
        layout.addWidget(self.sample_text)
        layout.addWidget(self.edit)
        layout.addWidget(self.button_sub)

        # Set dialog layout
        self.setLayout(layout)
        # Add button signal to greetings slot
        self.wtf = self.button_sub.clicked.connect(self.submit)
        print(self.wtf)

    # Greets the user
    def submit(self):
        return 'ok'


def counter(time_wait):
    for sec in range(time_wait + 1):
        time.sleep(1)


def run(text):
    print(text)
    counter(3)
    start_time = datetime.datetime.now()
    user_input = input('Start:\n')
    end_time = datetime.datetime.now()
    time_diff = end_time - start_time
    if user_input == text:
        print('Correct!')
    else:
        print('Input text does not match the given text')
    print(f'Time taken {time_diff.seconds},{time_diff.microseconds} s')


text_sample = ('There are only two ways to live your life. One is as though nothing is a miracle.'
               ' The other is as though everything is a miracle.')

if __name__ == '__main__':
    # run(text_sample)

    # Create the Qt Application
    app = QApplication(sys.argv)
    # Create and show the form
    form = Form(text_sample)
    form.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
