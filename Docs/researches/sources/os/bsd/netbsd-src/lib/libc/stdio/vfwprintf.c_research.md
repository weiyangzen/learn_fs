# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vfwprintf.c

Contains the shared implementation for wide `vfwprintf` and, when included with `NARROW`, narrow `vfprintf`. It handles locking wrappers, unbuffered-stream optimization through `__sbprintf()`, output batching for narrow streams, direct wide output for wide streams, integer conversion with grouping, string conversion between multibyte and wide forms, floating-point formatting via dtoa/hdtoa helpers, padding, prefixes, precision, width, `%n`, and positional arguments.

Key internal helpers include `__ultoa()`, `__ujtoa()`, `__mbsconv()`, `__wcsconv()`, `__find_arguments()`, `__grow_type_table()`, and `exponent()`. Risks and complexity concentrate in shared preprocessor-mode behavior, positional argument table construction, locale grouping/decimal output, conversion allocation failures, and return-count overflow handling.
