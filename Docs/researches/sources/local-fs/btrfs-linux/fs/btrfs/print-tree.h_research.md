# File Research: sources/local-fs/btrfs-linux/fs/btrfs/print-tree.h

This header exposes Btrfs metadata printing helpers used by diagnostic code.

Definitions:
- `BTRFS_ROOT_NAME_BUF_LEN` is `48`, sized for root names plus extra relocation-root offset text.
- Forward declares `struct extent_buffer` and `struct btrfs_key`.

Public interface:
- `void btrfs_print_leaf(const struct extent_buffer *l);`
- `void btrfs_print_tree(const struct extent_buffer *c, bool follow);`
- `const char *btrfs_root_name(const struct btrfs_key *key, char *buf);`

Role in the module:
- Keeps print-tree callers independent from the implementation details in `print-tree.c`.
- Provides the buffer-size contract required by `btrfs_root_name()`.
