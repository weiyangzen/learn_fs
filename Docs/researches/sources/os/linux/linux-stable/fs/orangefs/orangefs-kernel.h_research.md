# File Research: sources/os/linux/linux-stable/fs/orangefs/orangefs-kernel.h

## Scope

This central OrangeFS kernel header declares subsystem data structures, global state, operation-state helpers, VFS operation exports, mount/device/cache interfaces, and utility macros.

## APIs And Structures

- Defines operation states and `struct orangefs_kernel_op_s` with tag, shared-memory slot state, upcall/downcall, completion, lock, attempts, and list node.
- Defines `struct orangefs_inode_s`, `struct orangefs_sb_info_s`, stats, cached xattr records, and write-range metadata.
- Provides `ORANGEFS_I()`, `ORANGEFS_SB()`, `orangefs_khandle_to_ino()`, root/handle match helpers, and `orangefs_set_timeout()`.
- Declares op cache, inode cache, waitqueue, superblock, file, inode, xattr, device, debug, and sysfs interfaces.
- Defines service operation flags and `get_interruptible_flag()`.

## Control Flow And Behavior

- `set_op_state_serviced()` marks an op serviced and completes its wait queue.
- `set_op_state_purged()` handles normal purged ops by completing waiters, while cancel ops are removed and released specially.
- `put_cancel()` frees a cancel op’s buffer slot and releases the op.
- `fill_default_sys_attrs()` fills owner/group/perms/time/mask for create-style upcalls from current fs credentials.

## Risks And Invariants

- Operation state bits coordinate request queue, in-progress hash, daemon restarts, cancellation, and waiting VFS callers.
- OrangeFS inode identity is fsid plus 128-bit handle; inode number is only a derived hash.
- `d_fsdata` stores dcache timeout as a cast jiffies value.
- Many globals are shared across files and require the documented spinlocks/mutexes.
