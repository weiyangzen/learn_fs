# File Research: sources/os/linux/linux/fs/openpromfs/inode.c

Implements `openpromfs`, a small virtual filesystem exposing OpenPROM/OpenFirmware device-tree nodes as directories and properties as files.

Key structures and behavior:
- `op_inode_info` embeds `struct inode` and records whether the inode represents a firmware node or property.
- `property_show()` renders property values as printable strings, chained string lists, byte hex, or 32-bit hex words.
- `openpromfs_lookup()` searches a node’s children first, then properties, creates/initializes inodes via `openprom_iget()`, and returns `d_splice_alias()`.
- `openpromfs_readdir()` emits `.`, `..`, child node directories, then property files, using firmware `unique_id` values as inode numbers.
- Root setup in `openprom_fill_super()` creates inode `0`, binds it to `of_find_node_by_path("/")`, installs directory ops, and creates the root dentry.
- Module init creates a slab cache for `op_inode_info`, registers filesystem type `openpromfs`, and teardown unregisters plus drains RCU before destroying the cache.

Notable details:
- `op_mutex` serializes traversal of firmware node/property lists.
- The `options/security-password` property is mode `0600`; other properties are readonly regular files.
- The filesystem is single-instance via `get_tree_single()`, anonymous-super backed, `SB_NOATIME`, and uses `simple_statfs`.
