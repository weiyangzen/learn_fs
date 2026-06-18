# File Research: sources/local-fs/mtd-utils/ubi-utils/include/libubigen.h

## Role
Public API for generating UBI image structures and writing UBI image volumes.

## Main Contents
- Defines `ubigen_info` for geometry, offsets, version, volume table size, and image sequence.
- Defines `ubigen_vol_info` for volume table/header generation.
- Declares initialization, empty volume table creation, EC/VID header initialization, volume table insertion, data volume writing, and layout volume writing.

## Interfaces And Dependencies
- Includes `stdint.h` and `mtd/ubi-media.h`.
- Implemented by `libubigen.c`.
- Used by `mtdinfo.c` and `ubiformat.c`.

## Notes
- Encapsulates UBI on-flash format calculations such as VID header offset, data offset, LEB size, and volume table size.
