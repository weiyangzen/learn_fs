# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/ebh_media.h

This header defines the on-flash eraseblock header layout for CHFS EBH metadata.

Key definitions:
- Little-endian aliases: `le16`, `le32`, `le64`.
- `CHFS_MAGIC_BITMASK`: eraseblock header magic.
- `CHFS_LID_NOT_DIRTY_BIT` and `CHFS_LID_DIRTY_BIT_MASK`: NOR logical-ID dirty-state encoding.
- Size macros for common erase counter header, NOR header, NAND header, and invalidation payload.
- `struct chfs_eb_ec_hdr`: common packed erase counter header with magic, CRC of erase count, and erase count.
- `struct chfs_nor_eb_hdr`: packed NOR header with CRC and LID. Dirty and invalidated states are encoded in the LID/CRC fields.
- `struct chfs_nand_eb_hdr`: packed NAND header with CRC, LID, and serial number for duplicate-resolution recovery.

Dependencies:
- Requires fixed-width integer types from includers.
- Used by `ebh.h` and `ebh.c` to interpret and write media headers.

Design notes:
- NOR recovery relies on the ability to change programmed bits from one to zero.
- NAND recovery relies on serial ordering rather than dirty-bit mutation.
