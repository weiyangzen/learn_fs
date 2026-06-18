# File Research: sources/os/bsd/freebsd-src/sys/sys/kcov.h

Defines the KCOV coverage device ABI. It includes coverage comparison encoding from `sys/coverage.h` and ioctl encoding from `sys/ioccom.h`.

Constants define maximum entries, entry size, trace modes for PC and comparisons, and ioctls to enable, disable, and set buffer size. Comparison flag helpers alias the generic coverage macros.
