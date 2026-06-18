# File Research: sources/local-fs/xfsprogs/repair/attr_repair.c

## Purpose

`attr_repair.c` validates and repairs XFS inode attribute forks during `xfs_repair`. It handles shortform attributes stored inside the inode, longform single-leaf attribute blocks, and node/tree-form attribute forks. It also validates legacy security attribute payloads such as ACLs, IRIX MAC labels, and IRIX capabilities.

The repair policy is conservative: shortform corruption can often be fixed by removing individual entries or truncating the shortform list, while most serious longform leaf/node corruption causes the whole attribute fork to be cleared and converted later to an empty shortform fork.

## Main Responsibilities

- Validate shortform attribute entry layout, sizes, flags, namespaces, names, incomplete flags, parent-pointer support, and selected root security values.
- Validate longform attribute root block 0 and distinguish leaf-form versus node-form attributes by magic number.
- Walk node-form attribute btrees from the leftmost leaf to the rightmost leaf with `da_util.c` path verification.
- Validate leaf entries, name/value heap ownership, hash ordering, sibling links, and header accounting.
- Read and validate remote attribute values where needed for root security attributes.
- Repair limited metadata fields such as shortform count/totsize, leaf `firstused`, leaf `usedbytes`, root sibling links, and stale interior hash values.
- Detect v5 metadata owner, block number, and UUID mismatches.

## Key Functions

- `process_attributes` is the public entry point. It dispatches by `di_aformat` to shortform, extents, or btree processing.
- `process_shortform_attr` validates and optionally mutates the in-inode shortform attribute list.
- `process_longform_attr` reads attribute block zero, checks the v5 header, and dispatches to leaf-root or node-root processing.
- `process_leaf_attr_block` validates one attribute leaf block and its heap/free-space usage.
- `process_leaf_attr_local` validates local leaf entries.
- `process_leaf_attr_remote` validates remote leaf entries and optionally reads remote value blocks.
- `process_node_attr` and `process_leaf_attr_level` traverse node-form attribute btrees.
- `valuecheck`, `xfs_acl_valid`, and `xfs_mac_valid` validate selected root security attribute values.

## Data and Control Flow

Shortform processing starts at `XFS_DFORK_APTR(dip)`, walks `xfs_attr_sf_entry` records, tracks the current byte size, and uses `memmove` to remove bad entries in modify mode. It recomputes `hdr->count` and `hdr->totsize`, then runs `libxfs_attr_shortform_verify` as a final verifier.

Longform processing maps file block zero through the repair `blkmap`, reads it with libxfs buffer verifiers, validates v5 fields, and uses the magic value to determine whether block zero is a leaf or an interior DA node. Leaf-root processing validates only block zero and clears root sibling pointers if needed. Node-root processing releases block zero and then uses `traverse_int_dablock`, `verify_da_path`, and `verify_final_da_path` to validate the full tree.

Leaf validation builds a byte-level free map for the filesystem block, marks the header and every leaf entry, then marks each local or remote name/value payload. Overlapping claims, invalid offsets, invalid flags, invalid namespaces, invalid names, bad hashes, unsupported parent pointers, and bad remote values all force failure.

## Dependencies

This file depends on:

- `bmap.c` for logical attribute block to filesystem block mapping.
- `da_util.c` for DA btree traversal and parent hash verification.
- libxfs attribute, DA node, buffer, and verifier helpers.
- global repair flags such as `no_modify`.
- repair warning/error reporting helpers.
- inode fork definitions from `dinode.h`.

## Important Invariants

- Shortform `totsize` must match the actual validated byte count.
- Shortform and longform entries may use exactly one valid namespace.
- Attribute names must pass `libxfs_attr_namecheck`.
- Parent-pointer attributes are invalid unless the filesystem supports parent pointers.
- Longform leaf hashes must match recomputed hashes and be nondecreasing across the walk.
- Leaf heap bytes and leaf entry bytes must not overlap.
- Node interior keys store the greatest hash value of the child block.
- v5 attribute blocks must have the expected owner inode, disk block number, and metadata UUID.

## Repair and Risk Notes

This file intentionally sacrifices longform attribute forks on many inconsistencies because partial deletion from longform leaves could require format conversion and remote value cleanup. The highest-risk logic is in `process_leaf_attr_block` and tree traversal, where byte-level heap accounting, hash propagation, remote value reads, sibling pointers, and no-modify behavior all interact. Remote attribute block ownership is not fully tracked here; the code validates content enough to decide whether the attribute fork should survive.
