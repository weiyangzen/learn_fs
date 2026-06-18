# File Research: sources/os/bsd/netbsd-src/sys/sys/ioctl.h

Public ioctl aggregation header. It pulls in terminal, disk, file, and socket ioctl definitions; defines old SunOS terminal-size aliases; declares passthrough ioctl commands for multiple emulations through `struct ioctl_pt`; and declares the userland `ioctl(int, unsigned long, ...)` prototype.

Compatibility handling is intentionally outside the include guard so `ioctl_compat.h` can be conditionally included for old tty APIs under `USE_OLD_TTY`, kernel compatibility options, or modular builds. ABI risks center on passthrough command namespace collisions and legacy terminal compatibility.
