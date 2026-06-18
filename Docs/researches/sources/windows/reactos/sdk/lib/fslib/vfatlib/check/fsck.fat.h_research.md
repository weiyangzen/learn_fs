# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fsck.fat.h

Central shared header for FAT checking structures, boot-sector layouts, directory-entry metadata, FAT state, and global checker flags.

Key elements:
- Provides ReactOS-specific endian and packing compatibility around the imported dosfstools-style checker code.
- Defines packed `boot_sector`, `boot_sector_16`, `info_sector`, and `DIR_ENT`.
- `DOS_FILE` is the in-memory directory tree node with short entry, long name, offsets, parent/next/first links.
- `DOS_FS` describes a mounted FAT filesystem: FAT geometry, root/data offsets, cluster counts, loaded FAT, cluster owners, label.
- FAT helper macros define EOF, bad-cluster, and extension-bit handling across FAT12/16/32 effective entry sizes.

Dependencies:
- Includes `msdos_fs.h`.
- Under ReactOS includes `rosglue.h` for checker globals and allocation/printing remaps.
- Non-ReactOS builds declare traditional dosfsck globals such as `interactive`, `rw`, `verbose`, `test`, and `mem_queue`.

Research notes:
- The header is the contract between low-level FAT parsing, directory scanning, LFN handling, and the top-level `VfatChkdsk`.
- `FAT_EXTD(fs)` depends on `fs->eff_fat_bits`; callers must initialize FAT geometry before interpreting FAT values.
