# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_attr_leaf.h

## Purpose
Declares the incore attr leaf header representation and the shortform, leaf, Btree growth/shrink, verification, and utility functions implemented by `xfs_attr_leaf.c`.

## Main Interfaces
- Incore header: `struct xfs_attr3_icleaf_hdr`, including links, magic, count, used bytes, 32-bit `firstused`, holes, and freemap entries.
- Shortform routines: create, replace, add, get, convert to leaf, remove, find, allfit, bytesfit, verify, and fork removal.
- Leaf routines: convert to node, convert to shortform, clear/set/flip incomplete flags, split, lookup, get value, add, remove, list.
- Shrink/growth helpers: leaf init, toosmall, unbalance.
- Utilities: last hash, leaf order, new entry size, leaf read, header conversion, header check.

## Data Model
The incore `firstused` is intentionally 32-bit, unlike the 16-bit on-disk field, so the code can represent maximum 64 KiB filesystem block sizes without overflow. Conversion helpers in the C file handle the special on-disk zero encoding for 64 KiB empty leaf blocks.

## Integration Points
Used by high-level attr operations in `xfs_attr.c`, attr listing, DA Btree code, inode fork conversion paths, and recovery/verification code that must inspect attr leaf blocks.

## Risks And Review Focus
- Prototype and struct changes must preserve compatibility with the on-disk leaf formats in `xfs_da_format.h`.
- The 32-bit incore `firstused` field is a correctness guard for 64 KiB block filesystems and should not be narrowed.
- Flag manipulation helpers are part of the delayed attr crash-consistency protocol.
