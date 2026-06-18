# File Research: sources/os/bsd/dragonflybsd/sys/sys/ptio.h

Pass-through device timeout ioctl definitions.

Key responsibilities:
- Includes `sys/ioccom.h`.
- Defines `PTIOCGETTIMEOUT` and `PTIOCSETTIMEOUT` ioctls for integer timeout control.

Important behavior:
- Very small ABI header for consumers that need to read or update pass-through timeout behavior.

Dependencies:
- Depends on ioctl encoding macros.

Notable risks:
- ioctl command letter `'T'` and numbers are ABI.
