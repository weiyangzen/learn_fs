# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ioccom.h

This header defines BSD-style ioctl command encoding macros.

Key definitions:
- `IOCPARM_MASK` limits encoded parameter size to 255 bytes.
- Direction/status bits: `IOC_VOID`, `IOC_OUT`, `IOC_IN`, `IOC_INOUT`.
- Macros:
  - `_IO(x, y)` for no-parameter ioctl.
  - `_IOR(x, y, t)` and `_IORN(x, y, t)` for copy-out with sizeof or explicit size.
  - `_IOW(x, y, t)` and `_IOWN(x, y, t)` for copy-in.
  - `_IOWR(x, y, t)` and `_IOWRN(x, y, t)` for bidirectional copy.

ABI notes:
- Encodes command in the lower word and size/direction in the upper word.
- Uses `0x20000000` to distinguish newer ioctls from older ones.

Relevance:
- Foundational ioctl ABI support. Used by headers such as `ipmi.h`.
