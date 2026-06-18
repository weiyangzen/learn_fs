# File Research: sources/os/bsd/openbsd-src/sys/sys/ioccom.h

This header defines ioctl command encoding macros.

Key definitions:
- Length/group extraction: `IOCPARM_MASK`, `IOCPARM_LEN`, `IOCBASECMD`, `IOCGROUP`.
- Maximum argument size: `IOCPARM_MAX` as `PAGE_SIZE`.
- Direction bits: `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`, `IOC_DIRMASK`.
- Encoding macros: `_IOC`, `_IO`, `_IOR`, `_IOW`, `_IOWR`.

Behavior and integration:
- Encodes direction, argument length, group, and number into an unsigned long command value.
- Used by nearly every ioctl ABI header.

Risk notes:
- Argument length is limited to 13 bits, but OpenBSD additionally caps ioctl args at `PAGE_SIZE`.
- `_IOWR` is named that way because `_IORW` conflicted historically with stdio.
