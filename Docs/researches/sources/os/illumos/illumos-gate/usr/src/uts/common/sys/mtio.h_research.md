# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mtio.h

Magnetic tape ioctl ABI and device minor-layout header.

Key responsibilities:
- Defines tape operation request structures `mtop` and 64-bit-count `mtlop`, plus 32-bit syscall variants.
- Defines tape operations such as write EOF, spacing, rewind/offline, retension, erase, EOM, record-size get/set, load, tell/seek, and media lock/unlock.
- Defines tape status structure `mtget` and 32-bit variant with type, device/error registers, residual, file/block position, flags, and blocking factor.
- Defines tape drive configuration structure `mtdrivetype`, density/speed arrays, retry and timeout settings.
- Defines persistent/recent SCSI error entry structures, request wrappers, and 32-bit variants.
- Defines tape status flags, a large set of legacy and generic tape type IDs, tape info table entry type, ioctl command numbers, media insert/eject state enum, default tape path, and minor-device encoding macros.

Dependencies:
- Includes `sys/types.h`; error entry references SCSI ARQ status types defined elsewhere.

Notable risks:
- This is old public device ABI with many legacy constants; changing command numbers or minor-bit macros breaks tools and drivers.
- User pointers in drive type and error-entry requests require safe copyin/copyout handling.
