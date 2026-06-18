# File Research: sources/os/bsd/dragonflybsd/sys/sys/mpt_ioctl.h

Userland ioctl ABI for LSI MPT-Fusion host adapter configuration and RAID actions.

Key responsibilities:
- Defines configuration page request structures for normal and extended MPI config pages.
- Defines `struct mpt_raid_action` for RAID action commands and returned status/data.
- Defines ioctl numbers for reading config headers/pages, reading extended config headers/pages, writing config pages, and issuing RAID actions.
- Provides 32-bit compatibility request structures and ioctl aliases on `__x86_64__`.

Important behavior:
- Header requests use the `header` fields to specify page type/version/number; buffer and length are unused.
- Page read/write requests expect `buf` and `len` to describe the whole page including header.
- All requests carry `page_address` and return IOC status.

Dependencies:
- Includes `sys/ioccom.h`.
- Depends on MPT MPI headers under `dev/disk/mpt/mpilib/`.

Notable risks:
- User pointers are embedded directly in ABI structures; compat structures are required for 32-bit callers on 64-bit kernels.
- ioctl command numbers are shared between native and compat variants, so dispatch code must select the correct layout by caller ABI.
