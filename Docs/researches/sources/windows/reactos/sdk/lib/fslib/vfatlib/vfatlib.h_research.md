# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/vfatlib.h

Primary internal header for the ReactOS VFAT library.

Key elements:
- Pulls in C runtime, Windows-compatible types, ReactOS NDK I/O/kernel/object/RTL APIs, and FMIFS callbacks.
- Includes checker API via `check/dosfsck.h`.
- Defines packed `FAT16_BOOT_SECTOR`, `FAT32_BOOT_SECTOR`, and `FAT32_FSINFO`.
- Defines FSInfo signatures.
- Defines `FORMAT_CONTEXT` for progress callbacks.
- Defines `FAT_TYPE` enum.
- Declares FAT12/16/32 formatters, progress update, and print functions.

Dependencies:
- Includes `common.h` after defining `FORMAT_CONTEXT`.
- Used by all VFAT formatter and checker integration files.

Research notes:
- The boot-sector structures are manually laid out with offsets in comments and packed to match on-disk format.
- This header is both formatter infrastructure and checker integration point, since it includes the imported check API.
