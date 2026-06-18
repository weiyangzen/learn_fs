# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.c

## Role

Implements `ntfscmp`, a read-only NTFS volume comparator that walks MFT records and compares inode open status, attribute presence, attribute headers, and attribute contents.

## Main Functions

- `parse_options()` requires two volumes and configures progress/verbose/debug output.
- `mount_volume()` checks mount state and mounts each volume read-only.
- `cmp_inodes()` iterates MFT record numbers and compares inode open results.
- `cmp_attributes()` walks attributes in type/name order and reports presence, walk errno, or content differences.
- `cmp_attribute()` compares attribute headers, opens matching attributes, checks sizes, and compares data.
- `cmp_attribute_data()` reads both attributes in `NTFS_BUF_SIZE` chunks.
- `cmp_index_allocation()` compares `$INDEX_ALLOCATION` attributes using their associated bitmap and MST-deprotected active index blocks.

## Dependencies

Uses libntfs-3g inode, attribute, MST, utility, and mount helpers via included project headers such as `mst.h`, `support.h`, `utils.h`, and `misc.h`.

## Important Behavior

The output strings are intentionally stable because external tools grep for them. Extension records are skipped as independent inode comparisons and handled through base-inode attribute walking. `$BadClus:$Bad` content comparison is skipped after header differences because mapping pairs already encode differences.

Index allocation comparison is bitmap-aware: inactive index blocks are not compared as live content. Attribute header comparison for non-resident attributes compares the full attribute record length, including padding, which the file comments call out as a FIXME relative to `ntfsinfo`.

## Research Notes

This utility is optimized for exact metadata-difference localization, not human-friendly diff output. It exits on serious read/pathological traversal errors but otherwise prints all detected differences.
