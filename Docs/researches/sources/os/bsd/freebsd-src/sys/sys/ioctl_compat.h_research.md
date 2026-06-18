# File Research: sources/os/bsd/freebsd-src/sys/sys/ioctl_compat.h

Defines legacy 4.3BSD tty ioctl compatibility structures and constants, guarded by `COMPAT_43TTY`. It errors if included without that compatibility option.

Structures include `tchars`, `ltchars`, and `sgttyb`. Ioctls cover old line discipline get/set, hangup, terminal parameters, special characters, local mode get/set/bit operations, and old console behavior.

The header also defines historical tty mode flags such as `RAW`, `CBREAK`, `ECHO`, parity bits, delay masks, local erase/echoing modes, `TOSTOP`, `FLUSHO`, `PASS8`, `PENDIN`, and related shifted local-mode aliases.
