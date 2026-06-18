# File Research: sources/os/bsd/openbsd-src/sys/sys/tprintf.h

Declares terminal-targeted kernel printf support. `tpr_t` is a session pointer wrapper. The API opens a target from a `struct proc`, closes it, and prints formatted kernel messages through `tprintf`.

The `tprintf` prototype carries a `__kprintf__` format attribute, giving compile-time format checking for kernel-style format strings.
