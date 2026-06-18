# File Research: sources/os/linux/linux/fs/orangefs/orangefs-cache.c

Implements the OrangeFS operation slab cache and operation tag allocation.

Key behavior:
- `op_cache_initialize()` creates a usercopy-aware `orangefs_op_cache` for `orangefs_kernel_op_s` objects and initializes tag counter at `100`.
- `get_opname_string()` maps operation type constants to human-readable debug names.
- `orangefs_new_tag()` assigns monotonically increasing nonzero tags under a spinlock.
- `op_alloc()` allocates and initializes operation state, list head, lock, completion, invalid default up/down call types, unique tag, requested upcall type, attempts, and current fsuid/fsgid credentials.
- `op_release()` frees operations back to the slab cache.

Important role:
- Operations allocated here are the fundamental units queued to userspace and completed by downcalls.
