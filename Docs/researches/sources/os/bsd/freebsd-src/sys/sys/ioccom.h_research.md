# File Research: sources/os/bsd/freebsd-src/sys/sys/ioccom.h

Defines FreeBSD ioctl command encoding. Command words contain direction bits, parameter length, command group, and command number. `IOCPARM_SHIFT`, `IOCPARM_MASK`, `IOCPARM_LEN`, `IOCBASECMD`, and `IOCGROUP` decode those fields.

Direction bits are `IOC_VOID`, `IOC_OUT`, `IOC_IN`, and `IOC_INOUT`; construction macros include `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `_IOWINT`. `_IOC_NEWLEN` and `_IOC_NEWTYPE` rewrite the encoded parameter size.

Kernel compatibility helpers include `IOCPARM_IVAL` for old ABI support and `_IOC_INVALID` as an impossible filler command. Userland gets the `ioctl(int, unsigned long, ...)` prototype outside standalone builds.
