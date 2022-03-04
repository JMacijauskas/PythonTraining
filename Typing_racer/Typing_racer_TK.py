import datetime
import time
import tkinter as tk

message = ('There are only two ways to live your life. One is as though nothing is a miracle.'
           ' The other is as though everything is a miracle.')

class SignalingEntry(tk.Entry):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)



class TypingRacer:
    def __init__(self, kinter: tk.Tk, text):
        self.ui = kinter
        self.sample_text = text
        self.start_time = 0
        self.end_time = 0

        # Tkinter main dialog config
        self.ui.title('Typing Racer')
        self.ui.geometry('600x400')
        self.ui.config(bg='#21AFC0')

        # canvas for items
        # self.widgets = tk.Canvas(self.ui, width=550, height=750, relief='raised', bg='#71A0C0')
        # self.widgets.pack()

        self.start_button = tk.Button(self.ui, text="Start", command=self.start, width=40)
        self.start_button.pack(expand=True)
        # self.widgets.create_window(10, 30, window=self.start_button)

        # config text boxes
        self.ref_text_box = tk.Text(
            self.ui,
            height=12,
            width=40,
            wrap='word'
        )
        self.ref_text_box.pack(expand=True)
        # self.widgets.create_window(20, 45, window=self.ref_text_box)
        self.ref_text_box.insert('end', self.sample_text)
        self.ref_text_box['state'] = 'disabled'
        # text_box.config(state='disabled')

        self.inp_text_box = tk.Entry(self.ui, width=150)
        self.inp_text_box.pack(expand=True)

        self.end_button = tk.Button(self.ui, text="End", command=self.end, width=40)
        self.end_button['state'] = 'disabled'
        self.end_button.pack(expand=True)

    def start(self):
        for sec in self.counter(1):
            self.start_button['text'] = f'Starting in {sec}...'

        # conditional state change
        self.start_button['state'] = 'disabled'
        self.end_button['state'] = 'active'
        # self.edit.setDisabled(False)
        # # start timer before focus is set on field (might avoid slight miliseconds error)
        self.start_time = datetime.datetime.now()
        # self.edit.setFocus()

    def check_text_with_change(self):
        input_text = self.edit.toPlainText()
        for letter_num, symbol in enumerate(input_text):
            if symbol != text_sample[letter_num]

                return
        if input_text == text_sample:
            self.end_time = self.end_time = datetime.datetime.now()

    def end(self):
        self.end_time = datetime.datetime.now()

    def counter(self, time_wait):
        for sec in range(time_wait + 1):
            yield time_wait - sec
            time.sleep(1)


if __name__ == '__main__':
    ui_interface = tk.Tk()
    TypingRacer(ui_interface, message)
    ui_interface.mainloop()
