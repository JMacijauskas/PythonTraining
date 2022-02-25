import datetime
import time

"""
display set text
start timer
prompt_input
end timer
check if correct
calculate time diff
return results (time diff, word count)
"""


def counter(time_wait):
    for sec in range(time_wait + 1):
        print(sec)
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
    run(text_sample)
