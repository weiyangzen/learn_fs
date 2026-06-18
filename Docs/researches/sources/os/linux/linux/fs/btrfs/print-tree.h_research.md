# File Research: sources/os/linux/linux/fs/btrfs/print-tree.h

This header exposes the Btrfs metadata printing interface.

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized for readable root names and relocation-root offset text.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Public API:
- `btrfs_print_leaf()` prints a Btrfs leaf extent buffer.
- `btrfs_print_tree()` prints a node/leaf tree, optionally following children.
- `btrfs_root_name()` formats a root key object ID into a readable name.

Role:
- Keeps diagnostic callers independent from `print-tree.c` internals.
- Provides the buffer-size contract used by `btrfs_root_name()`.
