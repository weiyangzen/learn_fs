# File Research: sources/local-fs/dosfstools/src/msdos_fs.h

Defines MS-DOS/FAT directory-entry constants and the packed 32-byte on-disk directory-entry structure used by dosfstools formatter/checker code.

Key elements:
- Fixed logical `SECTOR_SIZE` of 512 for directory-entry density constants.
- Directory-entry density helpers:
  - `MSDOS_DPS`
  - `MSDOS_DPS_BITS`
  - `MSDOS_DIR_BITS`
- FAT attribute constants:
  - `ATTR_NONE`
  - `ATTR_RO`
  - `ATTR_HIDDEN`
  - `ATTR_SYS`
  - `ATTR_VOLUME`
  - `ATTR_DIR`
  - `ATTR_ARCH`
- `ATTR_UNUSED` identifies attribute bits copied as-is.
- `DELETED_FLAG` and `IS_FREE` classify free/deleted directory slots.
- 8.3 name constants:
  - `MSDOS_NAME`
  - `MSDOS_DOT`
  - `MSDOS_DOTDOT`
- `struct msdos_dir_entry` maps the FAT short directory entry, including name, attributes, timestamps, high/low start cluster fields, and file size.

Dependencies:
- Includes `<stdint.h>`.
- Uses GCC `__attribute__((packed))` to preserve on-disk layout.

Research notes:
- The structure is shared by code that needs direct FAT directory-entry serialization.
- `SECTOR_SIZE` here is a fixed directory helper constant; `mkfs.fat.c` separately supports user/device logical sector sizes.
- `IS_FREE` treats both a zero first byte and `0xe5` as free/deleted slot markers.
