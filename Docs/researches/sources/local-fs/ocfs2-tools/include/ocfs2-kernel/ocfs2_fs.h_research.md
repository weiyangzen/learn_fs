# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_fs.h

## Purpose

Defines the OCFS2 on-disk filesystem format shared between kernel-derived headers and userspace tooling. This is the central ABI contract for superblocks, inodes, extents, allocation groups, directory indexing, xattrs, quotas, refcount trees, feature flags, and helper layout calculations.

## Main Contents

- Filesystem identity and layout constants: revision levels, superblock location, min/max block and cluster sizes, magic number, object signatures, volume UUID/label lengths, and slot limits.
- Feature bit definitions split into compatible, read-only-compatible, and incompatible sets, plus tool-specific transitional flags such as heartbeat-only devices, resize/tunefs-in-progress, local mount, sparse allocation, inline data, userspace stack, xattrs, metadata ECC, indexed directories, refcount trees, discontiguous block groups, clusterinfo, and append direct I/O.
- Inode flag and dynamic-feature definitions, including system inode roles, inline data/xattr state, indexed directories, refcounted files, and ext-style user-visible attributes.
- System inode enumeration and static metadata table mapping each system inode type to its name template, inode flags, and mode.
- Complete disk structures for extents, chains, truncate logs, extent blocks, slot maps, cluster info, superblock payload, local allocation bitmaps, inline data, dinodes, directory entries, directory trailers, indexed-directory roots/leaves, allocation groups, refcount trees, xattr records/blocks/trees, and global/local quota records.
- Kernel and userspace inline helpers for calculating record capacities per block, backup superblock locations, local alloc size, group bitmap size, xattr/refcount capacity, system inode names, directory entry types, and discontiguous group detection.

## Dependencies and Integration

- Relies on Linux-style integer/endian types (`__le16`, `__le32`, `__le64`, etc.) and POSIX mode constants.
- Included by the public userspace header `include/ocfs2/ocfs2.h`, which defines `OCFS2_SB(sb)` for tools and exposes helpers to libocfs2 callers.
- Mirrors kernel structure layout: many comments specify exact offsets and the expectation that structures fit within OCFS2's smallest block size.

## Research Notes

- This header is both data model and compatibility policy. Incorrect changes would break disk format compatibility.
- The userspace branch of inline helpers intentionally works on raw little-endian values already swapped to CPU format by libocfs2.
- Several structures use flexible zero-length arrays and unions to preserve exact on-disk placement.
- Feature support macros define what the filesystem driver supports, while libocfs2 expands support to include tools-only states such as heartbeat devices and interrupted tunefs operations.
