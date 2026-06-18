# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/ocfs2.h

## Purpose

Primary public libocfs2 header. It exposes filesystem state types, I/O channels, metadata APIs, allocation helpers, directory and inode operations, cluster/DLM integration, quota handling, feature parsing, xattr/refcount support, metadata ECC, and convenience conversions.

## Main Contents

- Feature support masks for libocfs2, expanding kernel-supported feature sets with tools-only states.
- `ocfs2_filesys`, cached inode/dquot, device, slot-map, quota, filesystem option, lookup result, and directory hash information structures.
- I/O channel lifecycle, cache management, block read/write, vector read, superblock read/write, o2image-aware reads, open/close/flush/free filesystem APIs.
- Inode, extent list, extent block, refcount block, group descriptor, directory block, dx root/leaf, xattr, quota, and journal byte-swapping declarations.
- Extent mapping/search, journal creation/features, metadata block read/write, refcount tree creation/attachment/COW/refcount mutation, directory iteration/link/unlink/lookup, inode scans, directory scans, and bitmap APIs.
- Device/mount/heartbeat discovery helpers and O2CB/DLM cluster lock lifecycle functions.
- Allocation APIs for chains, inodes, directories, extents, clusters, truncation, unwritten extents, and backup superblocks.
- Quota APIs for local/global quota file initialization, dquot hash management, usage computation, and applying quota changes.
- Metadata ECC compute/validate APIs and low-level block check helpers.
- Lock resource encode/decode and printable lock helpers.
- Feature string formatting/parsing, feature-level merging, and feature iteration helpers.
- Inline conversions between clusters, blocks, and bytes; cluster group calculations; feature predicates; extent record cluster accessors; swap-barrier guard; type-checked min/max macros; and deprecated extent/block iterator declarations.

## Dependencies and Integration

- Includes kernel-derived OCFS2 headers, O2DLm/O2CB headers, generated error table headers, JBD2 definitions, lock IDs, and ioctl definitions.
- Defines `OCFS2_SB(sb)` for userspace to reuse kernel-style feature macros from `ocfs2_fs.h`.
- This header is the main contract consumed by ocfs2-tools programs such as mkfs, fsck, debugfs, tunefs, mounted, and o2image.

## Research Notes

- The header mixes stable public API, internal-ish libocfs2 support, and deprecated iterators, reflecting a broad shared library surface.
- Inline conversion helpers saturate on overflow in several paths but explicitly state callers remain responsible for preventing ambiguity where max values are valid.
- Feature predicates operate on already CPU-order superblock values.
- Many APIs accept raw block buffers and require callers to maintain correct swapping and metadata ECC handling.
