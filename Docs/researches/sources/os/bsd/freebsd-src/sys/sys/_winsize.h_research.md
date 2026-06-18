# File Research: sources/os/bsd/freebsd-src/sys/sys/_winsize.h

Terminal window size structure.

Key elements:
- Defines `struct winsize` with row, column, horizontal pixels, and vertical pixels.

Dependencies:
- None explicit.

Research notes:
- Kernel stores the structure to present a consistent tty ioctl ABI but does not otherwise use the values.
- Peripheral to filesystem scope, but part of shared system ABI headers.
