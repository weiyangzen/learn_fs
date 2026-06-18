# File Research: sources/os/bsd/openbsd-src/sys/sys/ioctl.h

This umbrella header exposes tty, file, and socket ioctl definitions plus the userland `ioctl` prototype.

Key includes:
- `<sys/ttycom.h>`
- `<sys/filio.h>`
- `<sys/sockio.h>`

Userland declaration:
- `int ioctl(int, unsigned long, ...);`

Risk notes:
- This file does not define ioctl encoding itself; command construction comes from `ioccom.h` through included headers.
- Inclusion order exposes broad ioctl namespaces to userland.
