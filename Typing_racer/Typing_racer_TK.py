import datetime
import time
import tkinter as tk
import threading

message = ('There are only two ways to live your life. One is as though nothing is a miracle.'
           ' The other is as though everything is a miracle.')


class TypingRacer:
    def __init__(self, kinter: tk.Tk, text: str):
        self.taken_time = None
        self.last_tag = ''
        self.started = False
        self.running = False
        self.ui = kinter
        self.sample_text = text
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
        self.hrs = tk.StringVar()
        self.hrs_field = tk.Entry(self.ui, textvariable=self.hrs, width=2, font='Helvetica 14')
        self.hrs_field.pack(expand=True)
        self.hrs.set('00')
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

        self.inp_text_box = tk.Entry(self.ui, width=150, state='disabled')
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
        if self.running:
            times = int(self.hrs.get()) * 3600 + int(self.mins.get()) * 60 + int(self.sec.get())
            while times > -1:
                minute, second = (times // 60, times % 60)
                hour = 0
                if minute > 60:
                    hour, minute = (minute // 60, minute % 60)
                self.sec.set(second)
                self.mins.set(minute)
                self.hrs.set(hour)

                # Update the time
                self.ui.update()
                time.sleep(1)
                if times == 0:
                    self.sec.set('00')
                    self.mins.set('00')
                    self.hrs.set('00')
                times += 1

    def start(self):
        self.started = True

    def check_text_in_thread(self):
        row_num = 1
        while True:
            tags = self.ref_text_box.tag_names()
            if len(tags) > 1:
                self.ref_text_box.tag_delete(self.last_tag)
            if self.running:
                time.sleep(0.2)
                input_text = self.inp_text_box.get()
                for letter_num, symbol in enumerate(input_text):
                    if symbol != self.sample_text[letter_num]:
                        start_tag = f'{row_num}.{letter_num}'
                        end_tag = f'{row_num}.{len(input_text)}'
                        tag_name = f'tag_{letter_num}'
                        self.ref_text_box.tag_add(tag_name, start_tag, end_tag)
                        self.ref_text_box.tag_config(tag_name, background="red", foreground="white")
                        self.last_tag = tag_name
                        # print(f'{letter_num}  {start_tag}  {end_tag} {self.ref_text_box.tag_names()}')
                        break

                if input_text == self.sample_text:
                    self.end()

    def end(self):
        self.end_time = self.end_time = datetime.datetime.now()
        self.running = False
        self.taken_time = self.end_time - self.start_time

    def button_counter(self):
        while True:
            if self.started:
                self.start_button['state'] = 'disabled'
                time_wait = 3
                for sec in range(time_wait + 1):
                    left_time = time_wait - sec
                    time.sleep(1)
                    self.start_button['text'] = f'Starting in {left_time}...'
                # conditional state change
                self.end_button['state'] = 'active'
                self.inp_text_box['state'] = 'normal'

                # # start timer before focus is set on field (might avoid slight miliseconds error)
                self.start_time = datetime.datetime.now()

                self.inp_text_box.focus_set()

                self.start_button['state'] = 'active'
                self.running = True
                self.started = False


if __name__ == '__main__':
    ui_interface = tk.Tk()
    TypingRacer(ui_interface, message)
    ui_interface.mainloop()
