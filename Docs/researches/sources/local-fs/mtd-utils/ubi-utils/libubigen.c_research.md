# File Research: sources/local-fs/mtd-utils/ubi-utils/libubigen.c

## Role
Implementation of UBI image-generation primitives.

## Main Behavior
- Computes default VID header offset, data offset, LEB size, max volume count, and volume table size.
- Creates an empty volume table with valid CRCs for every record.
- Adds volume table records with reserved PEB count, alignment, type, data padding, flags, name, and CRC.
- Initializes EC and VID headers with UBI magic, version, erase counter, offsets, sequence, volume metadata, and CRCs.
- Writes regular volume data as full PEB records with EC/VID headers and `0xFF` padding.
- Writes two layout volume copies at selected PEBs.

## Interfaces And Dependencies
- Implements `include/libubigen.h`.
- Uses UBI media definitions, endian conversions, and `mtd_crc32`.
- Uses `common.h` diagnostics.

## Notes
- Static volume VID headers include data size, used EBs, and data CRC.
- Dynamic volume VID headers ignore static-only data parameters.
