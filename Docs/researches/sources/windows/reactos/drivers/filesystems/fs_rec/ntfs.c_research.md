# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/ntfs.c

This file implements the NTFS recognizer. It detects NTFS by checking whether the boot-sector OEM field is exactly `NTFS    `.

`FsRecIsNtfsVolume` ignores the supplied sector size and sector count and only validates the eight-byte OEM signature in `PACKED_BOOT_SECTOR`.

`FsRecNtfsFsControl` handles two minor functions:
- `IRP_MN_MOUNT_VOLUME`: gets the target device sector size and sector count, then attempts to read 512 bytes at the primary boot sector, midpoint sector, and final sector. If any read succeeds and the signature matches, it returns `STATUS_FS_DRIVER_REQUIRED`.
- `IRP_MN_LOAD_FILE_SYSTEM`: asks the recognizer core to load `\Registry\Machine\System\CurrentControlSet\Services\Ntfs`.

The midpoint and last-sector fallback reflects NTFS backup boot-sector probing. If none of the reads recognize NTFS, the default result is `STATUS_UNRECOGNIZED_VOLUME`.

Research notes:
- Detection is intentionally lightweight and signature-only.
- The recognizer frees the boot-sector buffer after the read attempts.
- The `else if` chain means later offsets are tried only when earlier reads fail, not when earlier reads succeed but do not match NTFS.
