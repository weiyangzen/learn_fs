# File Research: sources/os/bsd/dragonflybsd/sys/sys/file2.h

`file2.h` provides kernel-only inline wrappers around `struct fileops`. It includes `file.h`.

The wrappers call file operations through `fp->f_ops`. Read, write, ioctl, and stat acquire a temporary reference with `fhold()` and release it with `fdrop()` around the operation. Close, shutdown, kqfilter, and seek directly dispatch to the underlying method.

This header centralizes safe fileops dispatch and protects operations that need the file object held during execution.
