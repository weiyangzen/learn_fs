# File Research: sources/os/bsd/netbsd-src/lib/libc/include/extern.h

Private libc umbrella declarations for internal symbols used across libc.

Includes:
- Process/environment globals: `__minbrk`, `__sigintr`, `environ`.
- Internal wrappers: `__getcwd`, `__getlogin`, `__setlogin`, `__posix_fadvise50`, `__sysctl`.
- Error/string helpers: `_strerror_lr`, `__strerror`, `__strsignal`.
- gdtoa helpers: `__dtoa`, `__freedtoa`, conditionally `__hldtoa`, `__ldtoa`, plus `__hdtoa`.
- malloc fork hooks.
- context/signal trampoline helpers.

Also defines `WIDE_DOUBLE` when `long double` differs from `double`.
