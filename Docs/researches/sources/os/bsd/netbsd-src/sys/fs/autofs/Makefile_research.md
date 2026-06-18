# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/Makefile

## Summary
Installs public AUTOFS headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/fs/autofs`.
- Installs `autofs_ioctl.h` and `autofs_mount.h`.
- Includes `bsd.kinc.mk`.

## Integration Notes
These headers define the mount argument and daemon ioctl ABI used by userland automount components.
