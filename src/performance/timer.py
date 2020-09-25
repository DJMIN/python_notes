# coding = utf-8
"""timer"""

import contextlib
import functools
import logging
import time

# 2 ways to make a python timer directly using functions


# 1. define a timer decorator
def timeit(func):
    """to monitor time performance of decorated functions"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        begin_time = time.time()
        res = func(*args, **kwargs)
        time_elapsed = round(time.time() - begin_time, 4)
        from src.tools.signature import calling_description
        info = calling_description(func, *args, **kwargs)
        print(f'{info} | {time_elapsed} sec')
        return res
    return wrapper


# or a more complicated decorator using loggers
def timeit_with_logger(log_func=print):
    """
    log function is defined here to allow user to use loggers
    e.x. log_func=print / log_func=logger.DEBUG
    """
    def timer_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            begin_time = time.time()
            res = func(*args, **kwargs)
            time_elapsed = round(time.time() - begin_time, 4)
            from src.tools.signature import calling_description
            info = calling_description(func, *args, **kwargs)
            log_func(f'{info} | {time_elapsed} sec')
            return res
        return wrapper
    return timer_wrapper


# register timer decorator to target function
@timeit
def sleep():
    time.sleep(1)


# when target function is called, timer result will be printed
sleep()
# output: sleep() | 1.000* sec


# 2. define a context manager
# also, context manager can take log_func as param
@contextlib.contextmanager
def timer(msg=None, log_func=print):
    """to monitor time performance of code inside"""
    begin_time = time.time()
    yield
    time_elapsed = round(time.time() - begin_time, 4)
    log_func(f"{msg or 'timer'} | {time_elapsed} sec")


# use timer to monitor target code chunk
with timer('test context manager'):
    time.sleep(1)
# output: test context manager | 1.000* sec


# timer can further be defined as a class to fit more situations
class Timer(object):
    """a timer class"""

    def __init__(self, name='timer', log_func=None):
        self.__init = None
        self.__last = None
        self.__name = name
        if log_func is not None:
            assert callable(log_func), 'log_func is not callable'
        self.__log_func = log_func
        self.reset()

    def reset(self):
        """by calling reset, init time stamp will be set to now"""
        now = time.time()
        self.__init = now
        self.__last = now

    def __output(self, msg):
        """make timer output via given logging function (if exists)"""
        if self.__log_func:
            self.__log_func(msg)

    def close(self):
        """while closing, output life timing"""
        time_elapsed = round(time.time() - self.__init, 4)
        self.__output(f'{self.__name} closed | whole life {time_elapsed} sec')

    def timeit(self, func):
        """
        this method allow timer to be used as decorator
        the decorator can also share basic settings of timer instance
            e.x. name, log_func
        to make code simpler, just use timeit_with_logger directly
        """
        return timeit_with_logger(self.__log_func)(func)

    def __enter__(self):
        """by defining __enter__ and __exit__, timer can be used as context manager"""
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def tic(self):
        """start timing within a function call"""
        self.__last = time.time()

    def toc(self, title=None):
        """stop timing and output timing result within a function call"""
        time_elapsed = round(time.time() - self.__last, 4)
        msg = f"{title or self.__name} | {time_elapsed} sec"
        self.__output(msg)
        self.__last = time.time()


# prepare a warning level stream logger for timer instance
logging.basicConfig(level=logging.DEBUG)
my_logger = logging.getLogger('timer_logger')

# create a warning level timer instance using logger just created
my_timer = Timer(name='test_timer', log_func=my_logger.debug)


# 1st usage - decorator
@my_timer.timeit  # use timer as decorator
def sleep_1():
    time.sleep(1)


sleep_1()
# output: DEBUG:timer_logger:sleep_1() | 1.000* sec


# 2nd usage - context manager
def sleep_2():
    with Timer(name='test_timer', log_func=my_logger.info):
        time.sleep(1)


sleep_2()
# output: INFO:timer_logger:test_timer closed | whole life 1.000* sec


# 3rd usage - on demand tic toc
def sleep_3():
    my_timer.tic()  # tic for 1st round sleep
    time.sleep(1)
    my_timer.toc('1st round sleep')  # toc for 1st round sleep, auto tic for 2nd round sleep
    time.sleep(1)
    my_timer.toc('2nd round sleep')  # toc for 2nd round sleep


sleep_3()
# output: DEBUG:timer_logger:1st round sleep | 1.000* sec
#         DEBUG:timer_logger:2nd round sleep | 1.000* sec


# now we can analyze time performance of different code
# and find out which pattern of code is more efficient
scale = 1E7

with timer('for loop'):
    output_1 = []
    for i in range(int(scale)):
        output_1.append(i ** 2)
    del output_1

with timer('map'):
    output_3 = list(map(lambda x: x ** 2, range(int(scale))))
    del output_3

with timer('list generator'):
    output_2 = [i ** 2 for i in range(int(scale))]
    del output_2

# typically, the efficiency order should be: list generator > map > for loop
# however, considering memory issue, a better approach is to make generator instead of making whole list
with timer('map (generator)'):
    output_4 = map(lambda x: x ** 2, range(int(scale)))
