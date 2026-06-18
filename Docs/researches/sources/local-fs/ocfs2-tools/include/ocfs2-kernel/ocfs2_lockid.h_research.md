# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/ocfs2_lockid.h

## Purpose

Defines OCFS2 distributed lock resource identifier layout, lock type enumeration, and mappings from lock types to compact characters and printable names.

## Main Contents

- Lock resource names are fixed at 32 bytes: one type character, six padding characters, 16 hex block-number characters, 8 hex generation characters, and a terminator.
- `enum ocfs2_lock_type` covers metadata, data, super, rename, read/write serialization, dentry, open, flock, quota info, NFS sync, orphan scan, and refcount locks.
- `ocfs2_lock_type_char()` converts enum values to single-character type codes.
- `ocfs2_lock_type_strings[]` and `ocfs2_lock_type_string()` provide human-readable labels.

## Dependencies and Integration

- Used by libocfs2 lock resource encoding/decoding declarations in `include/ocfs2/ocfs2.h`.
- Kernel builds assert valid type indexes with `BUG_ON`; userspace builds return array entries directly.

## Research Notes

- The string array is static in a header, so each translation unit gets its own copy.
- Lock type codes are part of cluster-visible resource naming and must remain stable.
