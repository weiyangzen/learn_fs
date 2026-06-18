# File Research: sources/os/linux/linux/fs/udf/misc.c

Purpose: shared UDF descriptor and extended-attribute helpers.

Key behavior:
- `udf_add_extendedattr()` inserts a UDF extended attribute into the inode-resident EA area, creating an `extendedAttrHeaderDesc` if absent, shifting allocation descriptors as needed, updating implementation/application attribute offsets, and rewriting descriptor CRC/checksum.
- `udf_get_extendedattr()` walks the EA area by `genericFormat.attrLength`, with checks for undersized elements and overrun, and returns an attribute matching type/subtype.
- `udf_read_tagged()` reads and validates a tagged descriptor block: location, tag checksum, descriptor version 2/3, CRC length bounded by block size, and CRC value.
- `udf_read_ptagged()` translates a logical block address through partition mapping before calling `udf_read_tagged()`.
- `udf_update_tag()`, `udf_new_tag()`, and `udf_tag_checksum()` centralize UDF tag CRC and checksum production.

Integration:
- Called by mount/descriptor parsing, allocation descriptor writers, directory entry handling, partition sparing table updates, and inode EA handling.
- Relies on `udf_get_lb_pblock()`, `crc_itu_t()`, endian helpers, and inode/superblock private state.

Risks and invariants:
- EA mutation assumes enough in-inode free space; the TODO notes FreeEASpace is not checked.
- Tag validation is a main corruption boundary: bad location, checksum, version, or CRC rejects the buffer.
- `0xFFFFFFFF` is used as an invalid block sentinel.
