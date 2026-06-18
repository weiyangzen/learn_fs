# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/624

## Purpose
This fixture validates a dentry lifetime bug during ramfs unmount: `BUG: Dentry still in use in unmount`.

## Important APIs, types, and functions
Key frames are `umount_check`, `d_walk`, `shrink_dcache_for_umount`, `generic_shutdown_super`, `kill_litter_super`, `ramfs_kill_sb`, `deactivate_locked_super`, `cleanup_mnt`, `task_work_run`, and `do_exit`.

## Control flow
A task exits, mount cleanup runs task work, ramfs shutdown walks dentries, and `umount_check` finds `.index` still referenced.

## State and persistence behavior
The raw line persists dentry name, reference count, and filesystem pair `[unmount of ramfs ramfs]`. No file-level mutable state exists.

## Dependencies and integration points
It tests VFS/dcache report parsing and alternate-title extraction containing filesystem-specific unmount context.

## Risks and test signals
The parser must keep the generic title while accepting the ramfs-specific alternate string.
