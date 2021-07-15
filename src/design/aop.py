# coding = utf-8
"""AOP - Aspect Oriented Programming"""
__all__ = ['Advice', 'Context', 'register']

import contextlib
import dataclasses
import functools
import inspect
import traceback

from typing import List, Callable, Any


@dataclasses.dataclass()
class Context:
    """
    函数运行的上下文管理器，包含函数运行的基本信息
    func: 待运行函数本身
    args: 待运行函数的位置参数
    kwargs: 待运行函数的字典参数
    success: 函数是否成功运行
    result: 函数运行结果（如成功）
    exception: 函数运行异常（如失败）
    throw: 如函数运行失败，是否抛出异常
    traceback_str: 用于输出异常的traceback字符串
    """
    func: Callable = dataclasses.field()
    args: tuple = dataclasses.field(default_factory=tuple)
    kwargs: dict = dataclasses.field(default_factory=dict)
    success: bool = dataclasses.field(default=False)
    result: Any = dataclasses.field(default=None)
    exception: Exception = dataclasses.field(default=None)
    throw: bool = dataclasses.field(default=True)

    @property
    def traceback_str(self) -> str:
        return ''.join(traceback.format_exception(
            type(self.exception),
            self.exception,
            self.exception.__traceback__,
        )).strip()


def register(advice: Callable, **kwargs):
    """
    将某个自定义函数作为被装饰函数的生命周期
    register是Advice.register的简化版，只需要通过定义函数就可以实现生命周期管理的功能
    某些情况下，register需要借助全局变量，而Advice.register可以使用实例的属性，避免全局变量的使用

    Parameters
    ----------
    advice: 自定义advice函数，要求第一个参数必须是context，函数逻辑必须包含yield
    kwargs: advice函数除context外，其余参数的值

    * 函数yield时，被装饰函数会被执行，其执行结果将被写入context.result或context.exception

    Examples
    --------
    创建自定义advice函数：
    >>> def my_advice(context: Context):
    >>>     ...
    >>>     yield
    >>>     ...

    注册到其他函数上：
    >>> @register(my_advice)
    >>> def my_func():
    >>>     ...
    """
    advice = contextlib.contextmanager(advice)

    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(*_args, **_kwargs):
            context = Context(func, _args, _kwargs)

            with advice(context, **kwargs):
                try:
                    res = context.func(
                        *context.args,
                        **context.kwargs,
                    )
                except Exception as e:
                    context.success = False
                    context.exception = e
                else:
                    context.success = True
                    context.result = res

            if not context.success and context.throw:
                raise context.exception
            return context.result

        return wrapped_func

    return decorator


class _MethodFilter:
    """装饰整个类时，对类方法的筛选器，包含正选（SelectionFilter）和反选（ExceptionFilter）"""
    def __init__(self, klass, filter_list):
        self.cls = klass
        self.list = filter_list

    @property
    def methods(self):
        raise NotImplementedError


class _SelectionFilter(_MethodFilter):
    """正选类方法筛选器（默认）"""
    @property
    def methods(self):
        for method_name in self.list:
            signature = getattr(self.cls, method_name)
            if _callable(signature):
                yield method_name


class _ExceptionFilter(_MethodFilter):
    """反选类方法筛选器（默认）"""
    @property
    def methods(self):
        for method_name, signature in inspect.getmembers(self.cls):
            if (not method_name.startswith('__')) and \
                    (method_name not in self.list) and \
                    _callable(signature):
                yield method_name


class Advice:
    """
    Advice用来定义一个函数或方法从开始运行到结束的全生命周期
    自定义编辑before/after/returning/throwing等生命周期函数
    创建实例后，实例可用作装饰器，被装饰的函数将按照实例所定义的生命周期来执行

    如果实例成功运行，其流程为：before -> run -> returning -> after
    如果实例运行异常，其流程为：before -> run -> throwing -> after

    支持自定义的初始化函数：用于输入配置或保存生命周期需用到的额外变量
    支持自定义类方法筛选器：构造自定义筛选器子类，并替换到FunctionLifeCycle的类或实例中
    """
    SelectionFilter = _SelectionFilter  # 默认正选类方法筛选器，可替换
    ExceptionFilter = _ExceptionFilter  # 默认反选类方法筛选器，可替换

    def before(self, context):
        """支持自定义的钩子函数：调用函数或方法前需执行的操作"""
        pass

    def after(self, context):
        """支持自定义的钩子函数：调用函数或方法后需执行的操作"""
        pass

    def returning(self, context):
        """支持自定义的钩子函数：函数或方法成功运行后的操作"""
        pass

    def throwing(self, context):
        """支持自定义的钩子函数：函数或方法运行报错后的操作"""
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
        >>> lc = Advice()

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
                context = Context(func, args, kwargs, throw=throw)
                return self._life_cycle(context)

            return wrapped_func

        return decorator

    def register_class(self,
                       selection: List[str] = None,
                       exception: List[str] = None,
                       throw: bool = True):
        """
        装饰一个类的方法，使其应用生命周期（声明时装饰，不可继承）
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
        创建advice对象：
        >>> advice = Advice()

        应用举例：
        >>> @advice.register_instance()
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
        装饰一个类的方法，使其应用生命周期（实例化时装饰，可继承）
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
        创建advice对象：
        >>> advice = Advice()

        应用举例：
        >>> @advice.register_instance()
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

    def _life_cycle(self, context):
        """实现生命周期"""
        self.before(context)
        try:
            res = context.func(*context.args, **context.kwargs)
        except Exception as exc:
            context.success = False
            context.exception = exc
            self.throwing(context)
            if context.throw:
                raise exc
        else:
            context.success = True
            context.result = res
            self.returning(context)
            return res
        finally:
            self.after(context)

    def _filter(self, cls, selection, exception):
        return self.SelectionFilter(cls, selection) if selection \
            else self.ExceptionFilter(cls, exception or [])


def _callable(obj):
    """判断是否为函数（包含未绑定方法）或绑定方法，将类过滤掉"""
    return inspect.isfunction(obj) or inspect.ismethod(obj)


if __name__ == '__main__':
    # 两个简单的例子
    try:
        from colorama import Fore
    except ImportError:
        class Fore:
            RED = '\033[0;31m'
            YELLOW = '\033[0;33m'
            RESET = '\033[0m'

    print(Fore.RED + '示例1：函数运行监控器')

    from collections import deque

    def func_name(func: Callable):
        if hasattr(func, '__self__'):  # 处理绑定方法
            return f'{func.__self__.__class__.__name__}.{func.__name__}'
        if hasattr(func, '__qualname__'):
            local_name = func.__qualname__.rsplit('<locals>.', 1)[-1]
            name_list = local_name.split('.')
            if len(name_list) > 1:  # 处理非绑定方法、静态方法或类方法
                return f'{name_list[-2]}.{name_list[-1]}'
        return func.__name__  # 处理函数

    def _test_1_class():
        """示例1基于Advice class的实现"""
        class Tracer(Advice):
            """函数运行监控器，在运行一个函数前输出<开始运行>，运行结束后输出<结束运行>"""

            def __init__(self):
                self.stack = deque()  # 创建队列，保存函数调用栈

            @property
            def stack_info(self):
                return ' -> '.join(self.stack)

            def before(self, context):
                self.stack.append(func_name(context.func))
                print(f'started running {self.stack_info}')

            def after(self, context):
                self.stack.pop()

            def returning(self, context):
                print(f'finished running {self.stack_info}')

            def throwing(self, context):
                print(f'failed on running {self.stack_info}')

        tracer = Tracer()

        @tracer.register_instance(throw=False)  # 装饰所有方法并继承
        class A:
            def run(self):
                print(self.__class__.__name__)

        class B(A):
            def main(self):
                self.run()
                raise RuntimeError('Expected Error')

        B().main()

    def _test_1_func():
        """示例1基于register函数的实现"""
        stack = deque()

        def trace_func(context: Context, throw: bool = True):
            context.throw = throw
            stack.append(func_name(context.func))
            stack_str = ' -> '.join(stack)
            print(f'started running {stack_str}')
            yield  # 这里开始执行被装饰的函数
            if context.success:
                print(f'finished running {stack_str}')
            else:
                print(f'failed on running {stack_str}')
            stack.pop()

        class A:
            @register(trace_func)
            def run(self):
                print(self.__class__.__name__)

        class B(A):
            @register(trace_func, throw=False)
            def main(self):
                self.run()
                raise RuntimeError('Expected Error')

        B().main()

    print(Fore.YELLOW + '\nAdvice类实现' + Fore.RESET)
    _test_1_class()
    print(Fore.YELLOW + '\nregister函数实现' + Fore.RESET)
    _test_1_func()

    print(Fore.RED + '\n\n示例2：定时任务异常提醒')

    def _test_2_class():
        """示例2基于Advice class的实现"""
        class ScheduledTask(Advice):
            """定时任务异常提醒，在任务出现异常时，通过邮件将异常信息发送给维护人员"""

            def __init__(self, email_to, email_cc=None):
                self.email_to = email_to
                self.email_cc = email_cc or []

            def throwing(self, context):
                # 将错误信息发送邮件通知，邮件部分省略
                print(f'exception sent to {self.email_to}')
                print(context.traceback_str)

        task_monitor = ScheduledTask(['xutongyan@citics.com'])

        @task_monitor.register(throw=False)  # 装饰任务，异常不抛出
        def task_main():
            raise RuntimeError('Expected Error')

        task_main()

    def _test_2_func():
        """示例1基于register函数的实现"""
        def task_func(context: Context, email_to, email_cc=None, throw=True):
            context.throw = throw
            yield  # 这里开始执行被装饰的函数
            if not context.success:
                # 将错误信息发送邮件通知，邮件部分省略
                print(f'exception sent to {email_to}')
                print(context.traceback_str)

        @register(task_func, email_to=['xutongyan@citics.com'], throw=False)  # 装饰任务，异常不抛出
        def task_main():
            raise RuntimeError('Expected Error')

        task_main()

    print(Fore.YELLOW + '\nAdvice类实现' + Fore.RESET)
    _test_2_class()
    print(Fore.YELLOW + '\nregister函数实现' + Fore.RESET)
    _test_2_func()
