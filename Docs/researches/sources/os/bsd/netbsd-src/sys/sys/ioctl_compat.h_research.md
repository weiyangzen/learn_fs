# File Research: sources/os/bsd/netbsd-src/sys/sys/ioctl_compat.h

Defines legacy BSD tty ioctl compatibility structures and constants. It includes `tchars`, `ltchars`, `sgttyb`, old line-discipline ioctls, local-mode ioctls, historical terminal flags such as `CBREAK`, `RAW`, `CRMOD`, delay masks, and local-mode shifted aliases.

This file preserves source and binary compatibility with older terminal driver interfaces and emulation layers. It relies on `sys/ioccom.h`, `sys/ttychars.h`, and `sys/ttydev.h`. Risks are compatibility fragility: values intentionally overlap termios-era constants and must not be casually renumbered.
