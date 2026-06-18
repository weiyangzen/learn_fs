# File Research: sources/os/bsd/freebsd-src/sys/sys/aac_ioctl.h

Adaptec AAC RAID controller ioctl definitions.

Key elements:
- Defines AAC queue statistics structures and `AACIO_STATS`.
- Defines Linux/Windows-derived `FSACTL_LNX_*` ioctl command numbers.
- Defines native BSD `FSACTL_*` ioctl encodings.
- Under `_KERNEL`, defines structures for revision checks, adapter FIB retrieval, disk queries, and feature reporting.

Dependencies:
- Requires ioctl macros and AAC driver protocol types from including context.

Research notes:
- Storage-management ABI for AAC RAID controllers.
- Includes compatibility support for Linux management applications and 32-bit adapter FIB pointers.
