# File Research: sources/os/linux/linux-stable/fs/btrfs/print-tree.h

This header exposes the Btrfs tree-printing helpers implemented in `print-tree.c`.

Public API:
- `void btrfs_print_leaf(const struct extent_buffer *l);`
- `void btrfs_print_tree(const struct extent_buffer *c, bool follow);`
- `const char *btrfs_root_name(const struct btrfs_key *key, char *buf);`

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized to hold a root name plus extra detail such as a relocation root offset.

Dependencies and declarations:
- Includes `<linux/types.h>`.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Role in the subsystem:
- Provides a small diagnostic interface for tree/leaf logging and root-name stringification without exposing implementation details of the printing logic.
