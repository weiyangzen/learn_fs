# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/625

## Purpose
This fixture covers the same dentry-still-in-use bug during ext4 loop-device unmount.

## Important APIs, types, and functions
Key frames include `umount_check`, `d_walk`, `shrink_dcache_for_umount`, `generic_shutdown_super`, `kill_block_super`, `deactivate_super`, `cleanup_mnt`, `task_work_run`, and `entry_SYSCALL_64_after_hwframe`.

## Control flow
An unmount syscall completes, task work releases the mount, and ext4 shutdown reaches `umount_check` with a still-referenced `.index` dentry.

## State and persistence behavior
The fixture persists the ext4-specific alternate title `[unmount of ext4 loop4]` and raw dentry identity.

## Dependencies and integration points
It complements report 624 and verifies filesystem-specific alternate extraction for VFS dcache warnings.

## Risks and test signals
The parser should deduplicate on the generic title but preserve the ext4 loop alternate for detail.
