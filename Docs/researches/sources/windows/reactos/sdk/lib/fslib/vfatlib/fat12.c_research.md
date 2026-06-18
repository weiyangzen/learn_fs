# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat12.c

Implements FAT12 volume formatting.

Key elements:
- Writes a FAT16-style boot-sector structure populated for FAT12.
- Initializes both FAT copies with FAT12 reserved cluster entries.
- Zeroes the fixed-size root directory.
- Chooses default cluster size: 4 KiB for fixed media, 512 bytes for removable/floppy media.
- Calculates FAT size from sector count, reserved sectors, root directory sectors, FAT count, and 12-bit entries.
- Supports full format by calling `FatWipeSectors` before writing metadata.

Dependencies:
- Uses `FAT16_BOOT_SECTOR` from `vfatlib.h`.
- Uses `CalcVolumeSerialNumber`, `GetShiftCount`, `FatWipeSectors`, and `UpdateProgress`.
- Uses `NtWriteFile` for direct metadata writes.

Research notes:
- Boot-sector signature is written at the end of the allocated sector buffer.
- Root entries are fixed at 512, matching classic FAT12/FAT16 root-directory layout.
- Label conversion truncates/pads to 11 OEM bytes.
