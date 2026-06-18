# File Research: sources/local-fs/ocfs2-tools/include/ocfs2-kernel/quota_tree.h

## Purpose

Defines the minimal quota tree disk header used by OCFS2 quota file handling.

## Main Contents

- `QT_TREEOFF` marks the quota tree start block offset.
- `struct qt_disk_dqdbheader` stores linked-list pointers for leaf blocks with free entries, a valid-entry count, and padding.

## Dependencies and Integration

- Included by `include/ocfs2/ocfs2.h`.
- Used with OCFS2 global quota block calculations and byte-swapping declarations.

## Research Notes

- The structure is intentionally small and disk-format oriented.
