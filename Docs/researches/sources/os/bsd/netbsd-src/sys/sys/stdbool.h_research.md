# File Research: sources/os/bsd/netbsd-src/sys/sys/stdbool.h

Read completely: 47 lines.

This header defines C99 boolean macros for non-C++ compilation: `bool` as `_Bool`, `true` as `1`, `false` as `0`, and `__bool_true_false_are_defined`.

Risks: no runtime behavior. It intentionally avoids redefining C++ built-in bool values.
