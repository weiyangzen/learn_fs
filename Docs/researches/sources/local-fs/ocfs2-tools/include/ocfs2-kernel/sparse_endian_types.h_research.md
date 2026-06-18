# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/sparse_endian_types.h

## Purpose

Provides userspace typedefs for Linux sparse endian types so kernel-derived OCFS2 headers can compile in ocfs2-tools.

## Main Contents

- Includes `<linux/types.h>`.
- Maps `__le16`, `__be16`, `__le32`, `__be32`, `__le64`, and `__be64` to their corresponding unsigned integer base types.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h` before including `ocfs2_fs.h`.

## Research Notes

- This is a compile-compatibility shim. It does not enforce endian correctness; byte swapping is handled elsewhere.
