# File Research: sources/teaching/os161/kern/include/stdarg.h

Defines kernel varargs support around GCC builtins. It typedefs `va_list` to `__va_list` under GCC and selects `__builtin_stdarg_start` for older GCC versions or `__builtin_va_start` for GCC 4.8 and newer. It also defines `va_arg`, `va_copy`, and `va_end`.

The header additionally declares kernel printf-family varargs entry points: `vkprintf`, `vsnprintf`, and the shared printf driver `__vprintf`, using `__PF` annotations from `cdefs.h`.

This file is a portability boundary between compiler ABI details and kernel formatting code. It assumes GCC-compatible builtins; non-GCC compilers would need parallel definitions.
