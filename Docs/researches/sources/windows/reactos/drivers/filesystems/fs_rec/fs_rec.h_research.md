# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fs_rec.h

This is the shared header for the ReactOS filesystem recognizer driver. It centralizes recognizer-wide constants, packed on-disk structures, filesystem type/state enums, device-extension layout, and function prototypes used by the individual recognizers.

The header defines allocation tag `FSREC_TAG`, UDFS probing offsets, local `ROUND_UP`/`ROUND_DOWN` helpers, and unaligned copy helpers used for FAT-style BIOS Parameter Block handling. It contains packed and unpacked BPB/boot-sector structures, plus minimal UDF anchor-volume descriptor structures.

`FILE_SYSTEM_TYPE` enumerates all recognizers supported by this driver: VFAT, NTFS, CDFS, UDFS, EXT, BTRFS, REISERFS, FFS, and FATX. `DEVICE_EXTENSION` stores recognizer state, filesystem type, and an alternate device object pointer.

The declared API surface includes per-filesystem FS control dispatchers, block-device helpers (`FsRecGetDeviceSectors`, `FsRecGetDeviceSectorSize`, `FsRecReadBlock`), and `FsRecLoadFileSystem`, which each recognizer uses after returning `STATUS_FS_DRIVER_REQUIRED`.

Important dependency: this header includes `ntifs.h`, so all declarations assume Windows kernel filesystem-driver types and calling conventions.

Research notes:
- This file is infrastructure, not recognition logic by itself.
- The packed structure definitions make unaligned on-disk access explicit.
- UDF descriptor definitions here overlap conceptually with `udfs.h`, which contains the VSD structure used by the UDF recognizer.
