# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat16.c

Implements FAT16 volume formatting.

Key elements:
- Writes FAT16 BPB/boot sector and signature.
- Initializes both FAT copies with media byte, reserved cluster, clean shutdown, and EOC markers.
- Zeroes the fixed root directory.
- Selects default cluster size by partition length: 1 KiB under 16 MiB, 2 KiB under 128 MiB, 4 KiB under 256 MiB, otherwise 8 KiB.
- Calculates FAT sectors for 16-bit entries.
- Supports quick and full format.

Dependencies:
- Uses shared VFAT boot-sector structures and helpers from `vfatlib.h`/`common.c`.
- Writes through `NtWriteFile`.

Research notes:
- Like FAT12, FAT16 uses a fixed root directory and two FAT copies.
- Assumes FAT16 formatting is selected only for partitions in an appropriate size range by `VfatFormat`.
