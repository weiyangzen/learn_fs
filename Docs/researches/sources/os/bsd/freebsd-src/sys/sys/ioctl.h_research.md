# File Research: sources/os/bsd/freebsd-src/sys/sys/ioctl.h

Userland umbrella header for ioctl definitions. It intentionally errors under `_KERNEL`, directing kernel code to include the specific `xxxio.h` header instead.

It includes `sys/ioccom.h` for ioctl encoding and then aggregates file, socket, and tty ioctl command headers: `filio.h`, `sockio.h`, and `ttycom.h`.
