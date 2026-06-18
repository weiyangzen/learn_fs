# File Research: sources/os/bsd/openbsd-src/sys/sys/ttycom.h

Defines tty ioctl ABI constants and small structures. `struct winsize` stores rows/columns/pixel size; `struct tstamps` controls timestamp reasons.

The ioctl set covers exclusivity, flushing, termios get/set, line discipline get/set, break/DTR/modem controls, process group/session, pty packet mode, remote mode, window size, user control mode, status, console/control tty, external processing, signal generation, drain, device flags, and timestamping. It also defines modem bit constants and line discipline numeric ids.
