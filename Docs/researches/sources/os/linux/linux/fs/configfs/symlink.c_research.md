# File Research: sources/os/linux/linux/fs/configfs/symlink.c

## Purpose
Implements configfs symlink semantics, which act as resolved object links that pin target config_items and notify client callbacks.

## Main Elements
- Path construction: `item_depth()`, `item_path_length()`, `fill_item_path()`, and `configfs_get_target_path()` build a relative symlink body from parent item to target item.
- Link creation: `create_link()` checks target readiness, increments target link count, computes symlink body, and calls `configfs_create_link()`.
- Target resolution: `get_target()` resolves the user-supplied symlink target path, requires it to be on the same configfs superblock, and returns a referenced config item.
- `configfs_symlink()`: validates parent item operations, temporarily unlocks the parent inode to resolve the target, calls client `allow_link()`, serializes with `configfs_symlink_mutex`, creates the link, and calls `drop_link()` on failure after allow.
- `configfs_unlink()`: removes link dirent/VFS link, calls client `drop_link()`, decrements target link count, and drops target dirent/item references.
- `configfs_symlink_inode_operations`: uses `simple_get_link` and configfs setattr.

## Dependencies And Integration
Works with `dir.c` for link dirent creation/removal and rmdir link-count checks. Client behavior is supplied by `ct_item_ops->allow_link()` and `drop_link()`.

## Risk Notes
The file explicitly documents unusual ABI semantics: symlink targets are resolved at syscall time and make targets busy from rmdir's perspective. Locking is delicate because target lookup cannot be done while holding the parent directory lock without deadlock risk.
