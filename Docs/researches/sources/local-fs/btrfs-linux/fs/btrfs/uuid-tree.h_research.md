# File Research: sources/local-fs/btrfs-linux/fs/btrfs/uuid-tree.h

Declares the Btrfs UUID tree management API.

Key declarations:
- `btrfs_uuid_tree_add()` and `btrfs_uuid_tree_remove()` update UUID/type to subid mappings inside a transaction.
- `btrfs_uuid_tree_check_overflow()` checks if an additional subid can fit in an existing UUID item.
- `btrfs_uuid_tree_iterate()` validates and cleans UUID tree contents.
- `btrfs_create_uuid_tree()` creates the UUID tree and starts initial population.
- `btrfs_uuid_scan_kthread()` is the worker entry point for scanning roots into the UUID tree.

Core mechanics:
- The header keeps transaction and filesystem structs opaque and exposes only the high-level UUID tree operations.
- UUID types are passed as `u8`, matching Btrfs key type values for subvolume and received-subvolume UUID entries.

Important invariants:
- Add/remove callers must supply an active transaction handle.
- The `uuid` pointer must address a full Btrfs UUID-sized byte array.
- `subid` is the root/subvolume id stored in the UUID tree item payload.

Filesystem relevance:
- This is the interface used by root/subvolume management code to maintain the on-disk UUID index.

Notable risks:
- The API assumes callers understand which UUID key type they are maintaining; type confusion would create valid-looking but semantically wrong index items.
