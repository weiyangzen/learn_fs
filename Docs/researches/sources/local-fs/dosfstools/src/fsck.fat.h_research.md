# File Research: sources/local-fs/dosfstools/src/fsck.fat.h

Central shared FAT filesystem structures, constants, and globals.

Key definitions:
- FAT/VFAT constants:
  - `VFAT_LN_ATTR`
  - dirty/surface-test flags
  - FAT16/FAT32 clean-shutdown and hard-error flags
- Packed on-disk structures:
  - `struct boot_sector`
  - `struct boot_sector_16`
  - `struct info_sector`
  - `DIR_ENT`
- Runtime structures:
  - `DOS_FILE`: directory tree node with short entry, optional LFN, offsets, parent/child links.
  - `FAT_ENTRY`: decoded FAT value plus FAT32 reserved high bits.
  - `DOS_FS`: parsed filesystem layout, FAT metadata, root/data positions, cluster size/count, FSINFO, FAT buffer, cluster owner table, serial, and label.
- Global variables shared by commands and modules:
  - `rw`, `list`, `verbose`, `test`, `no_spaces_in_sfns`
  - `fat_table`
  - `only_uppercase_label`
  - `n_files`
  - `mem_queue`
- FAT marker macros:
  - `FAT_EOF`
  - `FAT_IS_EOF`
  - `FAT_BAD`
  - `FAT_MIN_BAD`
  - `FAT_MAX_BAD`
  - `FAT_IS_BAD`
  - `FAT_EXTD`

Role:
- This header is the core contract between boot parsing, FAT manipulation, directory checking, LFN handling, CLI drivers, and I/O.
