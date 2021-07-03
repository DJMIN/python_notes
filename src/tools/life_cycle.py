# coding = utf-8
"""life_cycle"""

import functools
import inspect

from typing import List


class FunctionLifeCycle:
    """
    FunctionLifeCycle用来定义一个函数从开始运行到结束的全生命周期
    自定义编辑before/after/returning/throwing等生命周期函数
    创建实例后，实例可用作装饰器，被装饰的函数将按照实例所定义的生命周期来执行

    如果实例成功运行，其流程为：before -> run -> returning -> after
    如果实例运行异常，其流程为：before -> run -> throwing -> after
    """

    def before(self, func, args, kwargs):
        """支持自定义的钩子函数：调用function或method前需执行的操作"""
        pass

    def after(self, func, args, kwargs):
        """支持自定义的钩子函数：调用function或method后需执行的操作"""
        pass

    def returning(self, res, func, args, kwargs):
        """支持自定义的钩子函数：function或method成功运行后的操作"""
        pass

    def throwing(self, exc, func, args, kwargs):
        """支持自定义的钩子函数：function或method运行报错后的操作"""
        pass

    def register(self, throw=True):
        """
        装饰一个函数或方法，使其应用生命周期

        Parameters
        ----------
        throw: 如果被装饰对象在运行期间出现异常，是否抛出

        Examples
        --------
        创建life cycle对象：
        >>> lc = FunctionLifeCycle()

        function应用举例：
        >>> @lc.register()
        >>> def my_func():
        >>>     ...

        method应用举例：
        >>> class MyClass:
        >>>     @lc.register()
        >>>     def my_method(self):
        >>>         ...
        """
        def decorator(func):
            if not _callable(func):
                raise TypeError(f'{func} not callable')

            @functools.wraps(func)
            def wrapped_func(*args, **kwargs):
                return self._life_cycle(func, args, kwargs, throw)

            return wrapped_func
        return decorator

    def register_class(self,
                       selection: List[str] = None,
                       exception: List[str] = None,
                       throw: bool = True):
        """
        装饰一个类的方法，使其应用生命周期
        在类被声明时即完成装饰，不会影响子类的独有方法（或重定义的方法）

        Parameters
        ----------
        selection: 如果不为None，则只装饰其中包含的方法（填写名称）
        exception: 如果不为None，则只装饰其中不包含的方法（填写名称）
        throw: 如果被装饰对象在运行期间出现异常，是否抛出
        * 如果selection和exception均为None，则装饰所有方法
        * 如果selection和exception均不为None，则以selection为准

        Examples
        --------
        创建life cycle对象：
        >>> lc = FunctionLifeCycle()

        应用举例：
        >>> @lc.register_instance()
        >>> class MyClass:
        >>>     ...
        """
        def decorated_class(cls):
            _args = (cls, selection, exception)
            method_filter = self._filter(*_args)
            add_func = self.register(throw)

            cls_name = cls.__name__
            cls_base = (cls,)
            cls_dict = dict(**cls.__dict__)
            for name in method_filter.methods:
                cls_dict[name] = add_func(cls_dict[name])
            return type(cls_name, cls_base, cls_dict)

        return decorated_class

    def register_instance(self,
                          selection: List[str] = None,
                          exception: List[str] = None,
                          throw: bool = True):
        """
        装饰一个类的方法，使其应用生命周期
        在实例初始化时才完成装饰，效果会被继承到子类

        Parameters
        ----------
        selection: 如果不为None，则只装饰其中包含的方法（填写名称）
        exception: 如果不为None，则只装饰其中不包含的方法（填写名称）
        throw: 如果被装饰对象在运行期间出现异常，是否抛出
        * 如果selection和exception均为None，则装饰所有方法
        * 如果selection和exception均不为None，则以selection为准

        Examples
        --------
        创建life cycle对象：
        >>> lc = FunctionLifeCycle()

        应用举例：
        >>> @lc.register_instance()
        >>> class MyClass:
        >>>     ...
        """
        def decorated_class(cls):
            add_func = self.register(throw)

            def new_init(obj, *args, **kwargs):
                cls.__init__(obj, *args, **kwargs)

                _args = (obj.__class__, selection, exception)
                method_filter = self._filter(*_args)

                for name in method_filter.methods:
                    method = getattr(obj, name)
                    traced_method = add_func(method)
                    setattr(obj, name, traced_method)

            cls_name = cls.__name__
            cls_base = (cls,)
            cls_dict = dict(**cls.__dict__)
            cls_dict['__init__'] = new_init
            return type(cls_name, cls_base, cls_dict)

        return decorated_class

    def _life_cycle(self, func, args, kwargs, throw):
        """实现生命周期"""
        _args = (func, args, kwargs)
        self.before(*_args)
        try:
            res = func(*args, **kwargs)
        except Exception as exc:
            self.throwing(exc, *_args)
            if throw:
                raise exc
        else:
            self.returning(res, *_args)
            return res
        finally:
            self.after(*_args)

    @staticmethod
    def _filter(cls, selection, exception):
        return _Selection(cls, selection) if selection \
            else _Exception(cls, exception or [])


def _callable(obj):
    """判断是否为函数（包含未绑定方法）或绑定方法，将类过滤掉"""
    return inspect.isfunction(obj) or inspect.ismethod(obj)


class _MethodFilter:
    def __init__(self, klass, filter_list):
        self.cls = klass
        self.list = filter_list

    @property
    def methods(self):
        raise NotImplementedError


class _Selection(_MethodFilter):

    @property
    def methods(self):
        for method_name in self.list:
            signature = getattr(self.cls, method_name)
            if _callable(signature):
                yield method_name


class _Exception(_MethodFilter):

    @property
    def methods(self):
        for method_name, signature in inspect.getmembers(self.cls):
            if (not method_name.startswith('__')) and \
                    (method_name not in self.list) and \
                    _callable(signature):
                yield method_name


if __name__ == '__main__':
    # 两个简单的例子

    class Tracer(FunctionLifeCycle):
        """函数运行监控器，在运行一个函数前输出<开始运行>，运行结束后输出<结束运行>"""

        def __init__(self):
            from collections import deque
            self.stack = deque()  # 创建队列，保存函数调用栈

        @staticmethod
        def func_name(func):
            if hasattr(func, '__self__'):  # 处理绑定方法
                return f'{func.__self__.__class__.__name__}.{func.__name__}'
            if hasattr(func, '__qualname__'):
                name_list = func.__qualname__.rsplit('<locals>.', 1)[-1].split('.')
                if len(name_list) > 1:  # 处理非绑定方法、静态方法或类方法
                    return f'{name_list[-2]}.{name_list[-1]}'
            return func.__name__  # 处理函数

        @property
        def stack_info(self):
            return ' -> '.join(self.stack)

        def before(self, func, args, kwargs):
            self.stack.append(self.func_name(func))
            print(f'start running {self.stack_info}')

        def after(self, func, args, kwargs):
            print(f'finish running {self.stack_info}')
            self.stack.pop()

    tracer = Tracer()

    @tracer.register_instance()  # 装饰所有方法并继承
    class A:
        def run(self):
            print(self.__class__.__name__)

    class B(A):
        def main(self):
            self.run()

    B().main()
    '''
    输出如下：
    start running B.main
    start running B.main -> B.run
    B
    finish running B.main -> B.run
    finish running B.main
    '''

    class ScheduledTask(FunctionLifeCycle):
        """定时任务异常通知，在任务出现异常时，通过邮件将异常信息发送给维护人员"""

        def __init__(self, email_to, email_cc=None):
            self.email_to = email_to
            self.email_cc = email_cc or []

        def throwing(self, exc, func, args, kwargs):
            # 将错误信息发送邮件通知，邮件部分省略
            print(f'exception sent to {self.email_to}')
            import traceback
            traceback.print_exc()

    task_monitor = ScheduledTask(['tongyan@xu.com'])

    @task_monitor.register(throw=False)  # 装饰任务，异常不抛出
    def task_main():
        raise RuntimeError('OH NO')

    task_main()
    '''
    输出如下：
    exception sent to ['tongyan@xu.com']
    Traceback (most recent call last):
      File ".../python_notes/src/tools/life_cycle.py", line 164, in _life_cycle
        res = func(*args, **kwargs)
      File ".../python_notes/src/tools/life_cycle.py", line 287, in task_main
        raise RuntimeError('OH NO')
    RuntimeError: OH NO
    '''
