# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/fat32.c

Implements FAT32 volume formatting.

Key elements:
- Writes primary and backup FAT32 boot sectors.
- Writes FSInfo sectors and backup FSInfo sectors.
- Initializes both FAT copies, including root directory cluster 2 as EOC.
- Writes an empty root directory cluster.
- Chooses default cluster size by partition length: 4 KiB under 8 GiB, 8 KiB under 16 GiB, 16 KiB under 32 GiB, otherwise 32 KiB.
- Computes `FATSectors32` and adjusts for the edge case where usable FAT entries are fewer than data clusters.

Dependencies:
- Uses `FAT32_BOOT_SECTOR`, `FAT32_FSINFO`, and FSInfo signature constants from `vfatlib.h`.
- Uses common serial, shift, wipe, and progress helpers.
- Uses `NtWriteFile`.

Research notes:
- Reserved sectors are fixed at 32, FSInfo at sector 1, backup boot at sector 6, root cluster at 2.
- `FsInfo->FreeCount` reserves the root cluster by subtracting one from computed free clusters.
- Formatter writes the backup FSInfo free count as unknown.
