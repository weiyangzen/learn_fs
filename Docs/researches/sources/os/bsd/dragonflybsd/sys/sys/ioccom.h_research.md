# File Research: sources/os/bsd/dragonflybsd/sys/sys/ioccom.h

`ioccom.h` defines the ioctl command encoding scheme. It reserves lower bits for group/number and upper bits for parameter size and direction.

It defines parameter-size masks, helpers `IOCPARM_LEN()`, `IOCBASECMD()`, `IOCGROUP()`, max parameter size, direction flags `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`, and construction macros `_IOC`, `_IO`, `_IOWINT`, `_IOR`, `_IOW`, and `_IOWR`.

For userland or virtual-kernel builds it declares `ioctl(int, unsigned long, ...)`. Many other headers in this group build their ioctl constants on this file.
