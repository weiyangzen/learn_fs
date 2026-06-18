# File Research: sources/local-fs/ocfs2-tools/include/ocfs2/kernel-rbtree.h

## Purpose

Provides a userspace copy of the Linux red-black tree interface used by OCFS2 tooling.

## Main Contents

- Defines `struct rb_node`, `struct rb_root`, red/black color constants, `RB_ROOT`, and `rb_entry`.
- Declares insert color fixup, erase, next/previous/first/last traversal, and node replacement functions.
- Defines `rb_link_node()` inline helper for linking a new red leaf.
- Includes a long usage example from the kernel header showing caller-provided search/insert logic.

## Dependencies and Integration

- Requires implementations of `rb_insert_color`, `rb_erase`, traversal, and replacement elsewhere in the userspace library.

## Research Notes

- The API intentionally avoids callbacks: callers provide tree ordering and invoke balancing primitives.
