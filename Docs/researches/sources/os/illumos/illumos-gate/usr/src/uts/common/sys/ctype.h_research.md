# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ctype.h

Kernel/simple ASCII character classification header. It defines macro predicates and inline boolean functions for digit, hex digit, lower/upper alpha, alphanumeric, printable, and whitespace tests.

Key elements:
- Macro predicates operate directly on ASCII character ranges and avoid locale dependence.
- `ISSPACE` recognizes space, tab, carriage return, and newline.
- Inline functions `isdigit`, `isxdigit`, `islower`, `isupper`, `isalpha`, `isalnum`, `isprint`, and `isspace` wrap the macros and return `boolean_t`.

Dependencies:
- Includes `sys/types.h` for `boolean_t` and `__GNU_INLINE`.
- Intended for kernel or system code that cannot or should not depend on libc locale-aware ctype behavior.

Research notes:
- The functions accept `char`, not `int`, and are ASCII-only; they are not drop-in locale-aware libc replacements.
- Macro arguments may be evaluated more than once in composed predicates such as `ISXDIGIT`, `ISALPHA`, and `ISALNUM`.
