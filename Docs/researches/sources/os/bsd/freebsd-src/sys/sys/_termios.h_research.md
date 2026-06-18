# File Research: sources/os/bsd/freebsd-src/sys/sys/_termios.h

Terminal I/O constants and `struct termios`.

Key elements:
- Defines control-character indexes, input/output/control/local flag bits, standard baud rates, and `NCCS`.
- Uses visibility gates for BSD, XSI, and POSIX-specific constants.
- Defines `tcflag_t`, `cc_t`, `speed_t`, and `struct termios`.

Dependencies:
- Relies on visibility macros from including context.

Research notes:
- Main ABI contract for terminal and tty behavior.
- Mostly peripheral to filesystem research, but terminal ioctl structures appear in broader kernel/user ABI work.
