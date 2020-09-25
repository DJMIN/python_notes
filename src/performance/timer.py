# coding = utf-8
"""timer"""

import functools
import logging
import time

# 2 ways to make a python timer directly using functions


# 1. define a timer decorator
def timer(func):
    """to monitor time performance of decorated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        print(f'function <{func.__name__}> takes '
              f'{round(end - start, 4)} sec')
        return res
    return wrapper


# register timer decorator to target function
@timer
def sleep():
    time.sleep(1)


# when target function is called, timer result will be printed
sleep()


# timer can be defined as a class to fit more situations


class Timer(object):
    """a timer class"""

    def __init__(self, logger=None, log_level=logging.INFO):
        self.__pre = time.time()
        self.__logger = logger
        self.__log_level = log_level

    def __output(self, msg):
        """make timer output via logger (if exists) or print"""
        if self.__logger:
            self.__logger.log(self.__log_level, msg)
        else:
            print(msg)

    def track(self, func):
        """
        this method allow timer to be used as decorator
        the decorator can also share basic settings of timer instance
            e.x. logger & log_level
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            end = time.time()
            msg = f'function <{func.__name__}> takes ' \
                  f'{round(end - start, 4)} sec'
            self.__output(msg)
            return res
        return wrapper

    def tic(self):
        """start timing within a function call"""
        self.__pre = time.time()

    def toc(self, title=None):
        """stop timing and output timing result within a function call"""
        now = time.time()
        msg = f'{title} takes {round(now - self.__pre, 4)} sec'
        self.__pre = now
        self.__output(msg)


# prepare a warning level stream logger for timer instance
my_logger = logging.getLogger('test_timer')
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.WARN)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
my_logger.addHandler(stream_handler)

# create a warning level timer instance using logger just created
my_timer = Timer(logger=my_logger, log_level=logging.WARN)


@my_timer.track  # use timer as decorator
def sleep_2():
    my_timer.tic()  # tic for 1st round sleep
    time.sleep(1)
    my_timer.toc('1st round sleep')  # toc for 1st round sleep, tic for 2nd round sleep
    time.sleep(1)
    my_timer.toc('2nd round sleep')  # toc for 2nd round sleep


# try the new timer
sleep_2()


# with the help of timer, now we can analyze time performance of different code easily
my_timer.tic()
output = []
for i in range(int(1E8)):
    output.append(i ** 2)
my_timer.toc('for loop')

output = [i ** 2 for i in range(int(1E8))]
my_timer.toc('list generator')
