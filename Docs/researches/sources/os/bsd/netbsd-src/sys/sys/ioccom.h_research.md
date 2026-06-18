# File Research: sources/os/bsd/netbsd-src/sys/sys/ioccom.h

Defines the canonical NetBSD ioctl command encoding. The upper bits encode direction and parameter length, while the lower bits encode command group and number. It exports `IOCPARM_LEN`, `IOCBASECMD`, `IOCGROUP`, direction flags, `_IOC`, `_IO`, `_IOR`, `_IOW`, `_IOWR`, and `IOCSNPRINTF`.

This header is foundational for device, filesystem, network, and compatibility ioctl ABIs. Risks are ABI immutability and size limits: command layouts must remain stable, and encoded argument lengths are limited by `IOCPARM_MASK` and `IOCPARM_MAX`.
