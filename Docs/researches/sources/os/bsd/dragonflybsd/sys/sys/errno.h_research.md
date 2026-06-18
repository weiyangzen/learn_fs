# File Research: sources/os/bsd/dragonflybsd/sys/sys/errno.h

`errno.h` defines the DragonFly errno namespace and the userland `errno` access pattern. In non-kernel, non-standalone builds it declares thread-local `errno`, `__errno_location()`, and maps `errno` either through an inline `__error()` or directly to `__errno_location()` for parser compatibility.

The file defines standard POSIX/BSD error constants from `EPERM` through `EOWNERDEAD`, with BSD-visible extras such as `ENOTBLK`, `EFTYPE`, `ENOATTR`, `EDOOFUS`, and `EASYNC`. `ELAST` is 99 under BSD visibility.

Kernel-only pseudo-errors include `ERESTART`, `EJUSTRETURN`, `ENOIOCTL`, and `EMOUNTEXIT`. These are internal syscall/control-flow indicators, not user-visible errno values.
