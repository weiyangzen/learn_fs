# File Research: sources/local-fs/kdave-linux/fs/btrfs/print-tree.h

## Purpose

Public declarations for Btrfs tree-printing diagnostics.

## Exports

- `BTRFS_ROOT_NAME_BUF_LEN`: fixed buffer length for formatted root names, including tree relocation offset text.
- `btrfs_print_leaf(const struct extent_buffer *l)`
- `btrfs_print_tree(const struct extent_buffer *c, bool follow)`
- `btrfs_root_name(const struct btrfs_key *key, char *buf)`

## Dependencies

Forward declares `struct extent_buffer` and `struct btrfs_key`, and includes Linux type definitions.

## Role in the System

Allows other Btrfs code to invoke tree/leaf debug dumping without exposing implementation details from `print-tree.c`.
