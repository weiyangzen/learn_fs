# File Research: sources/os/linux/linux-stable/fs/udf/partition.c

## Summary
Translates UDF logical partition blocks to physical blocks for plain, virtual/VAT, sparable, and metadata partition maps, and updates sparing tables for relocated blocks.

## Main Responsibilities
- Implements generic `udf_get_pblock()` dispatch through partition-map-specific translation callbacks.
- Translates UDF 1.50/2.00 virtual partitions through the VAT inode.
- Translates sparable partitions by consulting sparing table entries for packet remapping.
- Relocates bad blocks by inserting or reusing sparing table entries.
- Translates metadata partition blocks through the metadata file, falling back to the mirror metadata file on failure.

## Important Behavior
VAT translation may read entries from inline VAT data or from VAT file blocks, then recursively translate through the referenced physical partition while rejecting self-recursion.

Metadata reads use `inode_bmap()` on metadata or mirror inodes, then map through the associated physical/sparable partition reference.

## Risks
Sparing relocation mutates all loaded sparing table copies under `s_alloc_mutex`; ordering and tag updates must stay consistent. Metadata fallback lazily loads the mirror inode and can return `0xFFFFFFFF` when both metadata sources fail.
