import datetime
import time
import tkinter as tk
import threading
from enum import Enum, auto

message = ('There are only two ways to live your life. One is as though nothing is a miracle.'
           ' The other is as though everything is a miracle.')

# TODO: enum  auto for states
# TODO: improve time counter
# TODO: fix threads active
# TODO: add space separation fro initial text
# TODO: Add teardown for new cycle
# TODO: Add statistics
# TODO: add super classes


class RacerStates(Enum):
    IDLE = auto()
    STARTED = auto()
    RUNNING = auto()
    FINISHED = auto()
    CANCELLED = auto()


class TypingRacer:
    def __init__(self, kinter: tk.Tk, text: str):
        self.row_num = 1
        self.taken_time = None
        self.last_tag = ''
        self.state = RacerStates.IDLE
        self.ui = kinter
        self.sample_text = text
        self.sample_words = text.split(' ')
        self.start_time = datetime.datetime.now()
        self.end_time = datetime.datetime.now()

        # Create Entry Widgets for HH MM SS
        self.sec = tk.StringVar()
        self.sec_field = tk.Entry(self.ui, textvariable=self.sec, width=2, font='Helvetica 14')
        self.sec_field.pack(expand=True)
        self.sec.set('00')
        self.mins = tk.StringVar()
        self.mins_field = tk.Entry(self.ui, textvariable=self.mins, width=2, font='Helvetica 14')
        self.mins_field.pack(expand=True)
        self.mins.set('00')

        # Tkinter main dialog config
        self.ui.title('Typing Racer')
        self.ui.geometry('600x400')
        self.ui.config(bg='#21AFC0')

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

        self.inp_text_box = tk.Entry(self.ui, width=30, state='disabled')
        self.inp_text_box.pack(expand=True)

        self.end_button = tk.Button(self.ui, text="End", command=self.end, width=40)
        self.end_button['state'] = 'disabled'
        self.end_button.pack(expand=True)

        # creating and activating threads with launch
        self.timer_thread = threading.Thread(target=self.countdown_timer, daemon=True)
        self.timer_thread.start()
        self.button_thread = threading.Thread(target=self.button_counter, daemon=True)
        self.button_thread.start()
        self.entry_chech_thread = threading.Thread(target=self.check_text_in_thread, daemon=True)
        self.entry_chech_thread.start()

    def countdown_timer(self):
        while True:
            if self.state != RacerStates.RUNNING:
                continue
            else:
                times = int(int(self.mins.get()) * 60 + int(self.sec.get()))
                while times > -1:
                    minute, second = (times // 60, times % 60)
                    if minute > 60:
                        hour, minute = (minute // 60, minute % 60)
                    self.sec.set(f'{second:02}')
                    self.mins.set(f'{minute:02}')

                    # Update the time
                    self.ui.update()
                    time.sleep(1)
                    if times == 0:
                        self.sec.set('00')
                        self.mins.set('00')
                    times += 1

    def start(self):
        self.state = RacerStates.STARTED

    def check_text_in_thread(self):
        while True:
            time.sleep(0.2)
            if self.state != RacerStates.RUNNING:
                continue
            input_text = self.inp_text_box.get()
            starting_index = 0
            for word in self.sample_words:
                current_tag_name, tag_start, tag_end = self.detect_tag(word, input_text, starting_index)
                if current_tag_name is '':
                    if current_tag_name != self.last_tag:
                        self.create_new_tag(current_tag_name, tag_start, tag_end)
                    tags = self.ref_text_box.tag_names()
                    for tag in tags:
                        self.ref_text_box.tag_delete(tag)
                if input_text == word + ' ':
                    starting_index += len(word)
                    self.inp_text_box.delete('start', 'end')
            else:
                self.state = RacerStates.FINISHED

    def detect_tag(self, ref_word, input_text, start_index):
        for letter_num, symbol in enumerate(input_text):
            if symbol != ref_word[letter_num]:
                start_tag = f'{self.row_num}.{start_index + letter_num}'
                end_tag = f'{self.row_num}.{start_index + len(input_text)}'
                tag_name = f'tag_{start_tag}{end_tag}'
                print(tag_name, start_tag, end_tag)
                return tag_name, start_tag, end_tag
        return '', '', ''

    def create_new_tag(self, tag_name, start_tag, end_tag):
        self.ref_text_box.tag_add(tag_name, start_tag, end_tag)
        self.ref_text_box.tag_config(tag_name, background="red", foreground="white")
        self.ref_text_box.tag_delete(self.last_tag)
        self.last_tag = tag_name

    def end(self):
        self.end_time = datetime.datetime.now()
        self.state = RacerStates.FINISHED
        self.taken_time = self.end_time - self.start_time

    def button_counter(self):
        while True:
            if self.state == RacerStates.STARTED:
                self.start_button['state'] = 'disabled'
                time_wait = 3
                for sec in range(time_wait + 1):
                    left_time = time_wait - sec
                    time.sleep(1)
                    self.start_button['text'] = f'Starting in {left_time}...'
                # conditional state change
                self.end_button['state'] = 'active'
                self.inp_text_box['state'] = 'normal'

                # start timer before focus is set on field (might avoid slight miliseconds error)
                self.start_time = datetime.datetime.now()

                self.inp_text_box.focus_set()

                self.start_button['state'] = 'active'
                self.state = RacerStates.RUNNING


if __name__ == '__main__':
    ui_interface = tk.Tk()
    TypingRacer(ui_interface, message)
    ui_interface.mainloop()
