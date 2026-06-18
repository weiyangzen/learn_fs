# File Research: sources/os/linux/linux/fs/udf/partition.c

Purpose: UDF logical-to-physical block translation and relocation helpers.

Key behavior:
- `udf_get_pblock()` dispatches through a partition-specific translation function or maps type 1 partitions as `partition_root + block + offset`.
- `udf_get_pblock_virt15()` and `udf_get_pblock_virt20()` translate through the Virtual Allocation Table inode, handling inline and block-backed VAT data.
- `udf_get_pblock_spar15()` maps sparable packets through the first available sparing table, returning replacement packet locations when present.
- `udf_relocate_blocks()` updates sparing table entries for a bad physical block, inserting or reusing packet remaps across mirrored sparing tables under `s_alloc_mutex`.
- `udf_get_pblock_meta25()` maps metadata partitions through the metadata file, falling back to the mirror metadata file if needed.

Integration:
- Used by descriptor reads, inode/block mapping, metadata partition access, free-space counting, and UDF directory/inode operations.
- Partition function pointers are installed by `super.c` while loading logical volume partition maps.

Risks and invariants:
- Invalid translation returns `0xFFFFFFFF`.
- VAT recursion is explicitly detected to avoid infinite translation loops.
- Metadata reads only accept recorded/allocated extents; missing main metadata can trigger mirror lazy loading.
- Sparing relocation assumes power-of-two packet length and valid sparing tables established during mount.
