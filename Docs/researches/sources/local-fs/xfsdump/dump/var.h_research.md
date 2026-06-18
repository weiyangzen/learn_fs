# File Research: sources/local-fs/xfsdump/dump/var.h

This small header declares the `/var/[lib/]xfsdump` helper abstraction.

Exports:
- `var_create(void)`: ensure xfsdump’s state directory path exists.
- `var_skip(uuid_t *dumped_fsidp, void (*cb)(xfs_ino_t ino))`: if the state directory is on the filesystem being dumped, call back for every inode below it so those inodes can be excluded.

Dependency:
- Requires `uuid_t` and `xfs_ino_t` from included project/system headers before use.
