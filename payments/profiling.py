# profiling.py
from line_profiler import LineProfiler
import functools

def profile_view(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = LineProfiler()
        profiler.add_function(func)
        profiler.enable_by_count()
        result = func(*args, **kwargs)
        profiler.disable_by_count()
        profiler.print_stats()
        return result
    return wrapper
