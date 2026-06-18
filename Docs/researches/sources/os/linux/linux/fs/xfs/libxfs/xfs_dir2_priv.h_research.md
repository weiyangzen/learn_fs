# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_priv.h

## Purpose

Defines private cross-file interfaces for XFS directory version 2/3 implementations, including in-core abstractions for on-disk leaf/free headers, prototypes for shortform, block, data, leaf, node, and readdir helpers, and inline size calculations for directory data records.

## Main Interfaces

- In-core header shims: `struct xfs_dir3_icleaf_hdr` and `struct xfs_dir3_icfree_hdr`.
- Generic directory helpers declared from `xfs_dir2.c`: CI hash/compare, grow inode, CI lookup result, hash/compare wrappers.
- Block/data/leaf/node/shortform operation prototypes used by generic dispatch.
- Inline record sizing: `xfs_dir2_data_unusedsize()` and `xfs_dir2_data_entsize()`.
- Shortform entry helpers for parent inode, entry inode, filetype, next-entry walking, verification, and format conversion.

## Control Flow And Behavior

The header isolates directory implementation files from v2/v3 on-disk header differences by exposing host-endian in-core leaf/free headers whose `ents` or `bests` pointer references the variable-position on-disk arrays. It also centralizes format-operation prototypes so generic code can dispatch to shortform, block, leaf, or node code without exposing each implementation's local helpers.

The inline data record size helpers round unused and active directory data records to XFS directory alignment. Active entry size accounts for the fixed entry prefix, name bytes, optional filetype byte, and trailing offset tag.

## State And Data Structures

`xfs_dir3_icleaf_hdr` carries sibling block numbers, magic, entry count, stale count, and a pointer to leaf entries. `xfs_dir3_icfree_hdr` carries free-block magic, first covered data block, valid/used counts, and a pointer to bests entries. Both are transient views over v2/v3 disk blocks.

## Dependencies

Depends on public XFS directory, DA btree, mount, inode, buffer, and transaction types declared by included compilation units. It is consumed by all directory implementation files and by code that needs specific format conversions.

## Risks And Invariants

- Prototypes here define tight coupling among directory format files; signature drift breaks generic dispatch.
- Size helpers must exactly match on-disk layout, optional filetype support, and alignment rules.
- In-core header pointers are aliases into buffers, so callers must not use them after buffer lifetime ends or after format-changing reallocations.
