# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/module.h

This is the central Linux-kernel compatibility header for the ReactOS/Ext2Fsd ext2 driver. Despite the name, it is not just module metadata: it supplies byte-order helpers, Linux-style error-pointer macros, module/init/export no-ops, spinlocks, wait queues, timers, page and buffer-head structures, NLS declarations, jiffies, pool allocation wrappers, slab-cache declarations, block I/O constants, and time/division helpers.

Key definitions and behavior:
- Includes `linux/types.h`, `linux/errno.h`, `linux/rbtree.h`, `linux/fs.h`, and `linux/log2.h`.
- Provides `offsetof`, `container_of`, endian conversion macros, `ntohl`/`ntohs`/`htonl`/`htons`, and `cpu_to_*`/`*_to_cpu` families assuming little-endian CPU.
- Maps `printk` to `DbgPrint`; defines Linux `KERN_*` log prefixes as string constants.
- Implements Linux `ERR_PTR`, `PTR_ERR`, `IS_ERR`, and `BUG_ON`/`WARN_ON` using NT-style casts and `assert`.
- Turns Linux module primitives into no-ops or local wrappers: `THIS_MODULE`, `MODULE_LICENSE`, `EXPORT_SYMBOL`, `try_module_get`, `module_put`, `module_init`, `module_exit`, `LOAD_MODULE`, and `UNLOAD_MODULE`.
- Defines `spinlock_t` around `KSPIN_LOCK` plus saved `KIRQL`; `spin_lock_irqsave` stores the acquired IRQL in the caller flag.
- Implements `set_bit`, `clear_bit`, `test_bit`, `test_and_set_bit`, and `test_and_clear_bit` using interlocked operations for mutations.
- Defines a minimal `task_struct`, `current`, scheduler stubs (`cond_resched`, `need_resched`, `yield`, `might_sleep`), and `mutex_t` over `FAST_MUTEX`.
- Declares wait-queue structures and functions implemented elsewhere (`init_waitqueue_head`, `wake_up`, `prepare_to_wait`, `finish_wait`, etc.).
- Defines `struct block_device` with NT device/file object fields plus buffer-head cache/tree fields.
- Defines `struct page`, page flag constants, and Linux page flag macros over bit operations.
- Defines `struct buffer_head`, buffer state bits, state helper macros, buffer cache APIs (`__getblk`, `__bread`, `brelse`, `submit_bh`, `sync_dirty_buffer`, extents-specific buffer helpers, etc.), and inline wrappers such as `sb_getblk`, `sb_bread`, `map_bh`, `wait_on_buffer`, and `lock_buffer`.
- Declares NLS table structure and registration/loading/UTF-8 conversion routines.
- Defines `jiffies` by querying `KeQueryTickCount` and scaling by `KeQueryTimeIncrement` to `HZ == 100`.
- Maps `kmalloc`/`kfree` to `Ext2AllocatePool`/`Ext2FreePool` using tag `'JBDM'`; declares slab-like `kmem_cache` APIs backed by NT lookaside lists.
- Provides Linux block operation constants (`READ`, `WRITE`, `READ_SYNC`, `WRITE_BARRIER`, etc.), timer comparison macros, `smp_rmb` no-op, and `do_div`.

Dependencies:
- Requires NT kernel headers and types indirectly via `linux/types.h`.
- Depends on driver-side implementations for buffer heads, wait queues, pool allocation, slab cache, NLS, block I/O, and page allocation.

Research notes:
- This header concentrates many compatibility APIs that would normally be split across Linux headers such as `module.h`, `spinlock.h`, `sched.h`, `slab.h`, `buffer_head.h`, `pagemap.h`, `nls.h`, and `timer.h`; the zero-byte sibling headers in this group likely exist only to satisfy include paths.
- `BITS_PER_LONG` is fixed at 32 in `types.h`, so bit helpers here operate in 32-bit chunks even on `_WIN64`; separate `CFS_BITS_PER_LONG` exists but is not used by these macros.
