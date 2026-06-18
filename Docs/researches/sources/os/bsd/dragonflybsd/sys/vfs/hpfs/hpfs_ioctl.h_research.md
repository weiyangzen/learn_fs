# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hpfs/hpfs_ioctl.h

Source read: complete file, 44 lines.

Purpose: Public HPFS ioctl definitions for querying inline extended attributes.

Key definitions:
- `struct hpfs_rdea` carries an EA index, returned EA size, and user buffer pointer.
- `HPFSIOCGEANUM` returns the number of EAs.
- `HPFSIOCGEASZ` queries the size of a specific EA.
- `HPFSIOCRDEA` reads EA name/value data into a caller buffer.

Integration:
- Implemented by `hpfs_ioctl()` in `hpfs_vnops.c`.
- Includes `<sys/ioccom.h>` for ioctl encoding macros.

Risks and review notes:
- The ioctl contract exposes a raw user pointer in `hpfs_rdea`; implementation must validate copyout behavior and size handling carefully.
