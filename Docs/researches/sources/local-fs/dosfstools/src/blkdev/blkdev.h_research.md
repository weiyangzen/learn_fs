# File Research: sources/local-fs/dosfstools/src/blkdev/blkdev.h

Public header for block-device helper functions and fallback ioctl definitions.

Contents:
- Defines `DEFAULT_SECTOR_SIZE` as 512.
- Provides Linux ioctl constants when system headers do not define them:
  - basic block ioctls such as `BLKGETSIZE`, `BLKSSZGET`, `BLKRRPART`
  - `BLKGETSIZE64`
  - topology ioctls such as `BLKIOMIN`, `BLKPBSZGET`
  - discard-zeroes and freeze/thaw constants
  - `CDROM_GET_CAPABILITY`
- Defines Darwin `BLKGETSIZE` alias to `DKIOCGETBLOCKCOUNT32` when applicable.
- Provides fallback `HDIO_GETGEO` and `struct hd_geometry` definition.
- Declares block-device query functions implemented in `blkdev.c`.
- Defines SCSI peripheral type constants and declares `blkdev_scsi_type_to_name()`.

Role in system:
- Supplies a portability layer for `device_info.c` and mkfs-side device probing.
- Keeps platform ioctl compatibility isolated from mkfs/fsck higher-level code.
