# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_leaf.c

## Purpose

`xfs_attr_leaf.c` implements XFS extended-attribute shortform storage and attr leaf-block operations for libxfs. It covers inline attr fork management, conversion between shortform/leaf/node formats, leaf block verification, sorted-hash lookup, insertion/removal, compaction, split/rebalance/join support, and `INCOMPLETE` flag handling for atomic replace and remote-value updates.

## Main Behavior

The file normalizes legacy and CRC-enabled attr leaf headers through `xfs_attr3_leaf_hdr_from_disk` and `xfs_attr3_leaf_hdr_to_disk`, using a 32-bit in-core `firstused` field so 64 KiB attr blocks can round-trip through 16-bit on-disk headers. Leaf verifiers check da block metadata, CRCs, owner fields, hash ordering, name/value bounds, remote entry validity, free-map alignment, bounds, and overlap.

Shortform attrs live inside the inode attr fork. The shortform code creates the fork, checks fork byte fit, finds/replaces/adds/removes entries, copies values, verifies packed inline layout, removes the attr fork when it becomes empty, and converts shortform attrs into a newly allocated leaf block. Parent-pointer attrs get special value matching and replacement handling.

Leaf blocks use a sorted entry array at the front of the block and a backward-growing name/value region at the end. `xfs_attr3_leaf_add` finds free space, compacts fragmented blocks when useful, and inserts local or remote entries. Local entries store name and value in the leaf; remote entries store only the name and create an incomplete placeholder with remote block fields filled later by remote-value code.

The file also supports leaf-to-node conversion, split-time rebalance, block ordering, leaf coalescing decisions, removal, unbalance into a sibling, last-hash extraction, and duplicate-hash lookup. Lookup returns `-EEXIST` for found and `-ENOATTR` for not found, while also recording the entry index or insertion point in `args->index`.

## Atomic Replace and Remote Values

`xfs_attr3_leaf_setflag`, `xfs_attr3_leaf_clearflag`, and `xfs_attr3_leaf_flipflags` manage visibility through `XFS_ATTR_INCOMPLETE`. Remote attrs remain incomplete until remote blocks are allocated and synchronously written. Replace can flip old/new entries in one transaction, including the case where they are in different leaf blocks.

## Dependencies and Risks

This file depends on libxfs da btree, bmap, transaction, inode fork, remote attr, health, tracing, and on-disk format definitions. Risky areas are `firstused` overflow conversion, free-map coalescing/overlap behavior, duplicate hashes, old/new index tracking during split and replace, shortform/leaf format transitions during logged operations, and ensuring incomplete remote entries are never exposed before their values are durable.
