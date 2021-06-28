# coding = utf-8
"""life_cycle"""

import functools
import inspect


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

    def add(self, throw=True):
        """
        装饰一个function或method，使其应用生命周期

        Parameters
        ----------
        throw: 如果被装饰对象在运行期间出现异常，是否抛出

        Examples
        --------
        创建life cycle对象：
        >>> lc = FunctionLifeCycle()

        function应用举例：
        >>> @lc.add()
        >>> def my_func():
        >>>     ...

        method应用举例：
        >>> class MyClass:
        >>>     @lc.add()
        >>>     def my_method(self):
        >>>         ...
        """
        def decorator(func):
            if not self._callable(func):
                raise TypeError(f'{func} not callable')

            @functools.wraps(func)
            def wrapped_func(*args, **kwargs):
                return self._life_cycle(func, args, kwargs, throw)

            return wrapped_func
        return decorator

    def add_class(self, selection=None, exception=None, throw=True):
        """
        装饰一个class里的method，使其应用生命周期

        Parameters
        ----------
        selection: 如果不为None，则只装饰其中包含的method（填写名称）
        exception: 如果不为None，则只装饰其中不包含的method（填写名称）
        throw: 如果被装饰对象在运行期间出现异常，是否抛出
        * 如果selection和exception均为None，则装饰所有method
        * 如果selection和exception均不为None，则以selection为准

        Examples
        --------
        创建life cycle对象：
        >>> lc = FunctionLifeCycle()

        应用举例：
        >>> @lc.add_class()
        >>> class MyClass:
        >>>     ...
        """
        add_func = functools.partial(self.add, throw)
        if selection:
            decorate_func = functools.partial(
                self._by_selection, add_func, selection)
        else:
            decorate_func = functools.partial(
                self._by_exception, add_func, exception or [])

        def decorated_class(cls):
            cls_name = cls.__name__
            cls_base = (cls,)
            cls_dict = dict(**cls.__dict__)

            def new_init(obj, *args, **kwargs):
                cls.__init__(obj, *args, **kwargs)
                decorate_func(obj)

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

    def _by_selection(self, func, selection, obj):
        for method_name in selection:
            signature = getattr(obj.__class__, method_name)
            if self._callable(signature):
                self._add_single_method(obj, method_name, func)

    def _by_exception(self, func, exception, obj):
        for method_name, signature in inspect.getmembers(obj.__class__):
            if (not method_name.startswith('__')) and \
                    (method_name not in exception) and \
                    self._callable(signature):
                self._add_single_method(obj, method_name, func)

    @staticmethod
    def _add_single_method(obj, method_name, func):
        method = getattr(obj, method_name)
        traced_method = func(method)
        setattr(obj, method_name, traced_method)

    @staticmethod
    def _callable(obj):
        """判断是否为function（包含unbound method）或bound method，滤掉class"""
        return inspect.isfunction(obj) or inspect.ismethod(obj)
