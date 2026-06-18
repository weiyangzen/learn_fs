# File Research: sources/os/linux/linux/fs/udf/udfend.h

Purpose: endian conversion helpers for UDF on-disk address and extent structures.

Key behavior:
- Converts logical block addresses between little-endian disk `lb_addr` and CPU `kernel_lb_addr`.
- Converts short allocation descriptors between `short_ad` and CPU form.
- Converts long allocation descriptors between `long_ad` and `kernel_long_ad`.
- Converts extent allocation descriptors to CPU form.

Integration:
- Used throughout UDF descriptor parsing, partition translation, directory entries, inode extents, and fileset/logical volume loading.

Risks and invariants:
- UDF disk structures are little-endian; all direct disk-to-CPU conversion should use these helpers or equivalent endian access.
