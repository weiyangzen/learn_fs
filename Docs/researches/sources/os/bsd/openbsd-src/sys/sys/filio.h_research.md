# File Research: sources/os/bsd/openbsd-src/sys/sys/filio.h

This header defines generic file-descriptor ioctl commands.

Key definitions:
- `FIOCLEX` and `FIONCLEX` for close-on-exec.
- `FIONREAD` for readable byte count.
- `FIONBIO` for nonblocking mode.
- `FIOASYNC` for async IO.
- `FIOSETOWN` and `FIOGETOWN` for signal owner.

Behavior and integration:
- Includes `<sys/ioccom.h>`.
- Included by `<sys/ioctl.h>` alongside tty and socket ioctl sets.

Risk notes:
- These ioctls are generic and may be implemented by multiple file types, so behavior depends on fileops/device support.
