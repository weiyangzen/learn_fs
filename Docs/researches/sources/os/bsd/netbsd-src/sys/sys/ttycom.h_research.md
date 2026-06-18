# File Research: sources/os/bsd/netbsd-src/sys/sys/ttycom.h

Read completely: 183 lines.

Defines tty ioctl ABI and terminal window-size structures.

Key elements:
- Always exposes `struct winsize` with rows, columns, and pixel dimensions.
- NetBSD/ioctl section defines `struct ptmget`, `/dev/ptm` path, modem bit constants, termios get/set ioctls, line discipline ioctls, break/DTR/pgrp/ioctl controls, pty packet mode bits, modem controls, window-size ioctls, controlling tty/console controls, queue-size controls, and device flag ioctls.
- Defines line discipline numbers such as `TTYDISC`, `SLIPDISC`, `PPPDISC`, `STRIPDISC`, and `HDLCDISC`.

Risks and notes:
- Ioctl command numbers and payload types are stable ABI.
- Visibility depends on `_NETBSD_SOURCE` or inclusion through `sys/ioctl.h`.
