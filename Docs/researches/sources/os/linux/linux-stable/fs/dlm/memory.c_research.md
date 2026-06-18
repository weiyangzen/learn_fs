# File Research: sources/os/linux/linux-stable/fs/dlm/memory.c

## Purpose
`memory.c` centralizes DLM allocation through slab caches and RCU-delayed frees.

## Cache Lifecycle
`dlm_memory_init()` creates caches for:
- lowcomms writequeue entries
- midcomms message handles
- lowcomms messages
- lock blocks (`dlm_lkb`)
- resource blocks (`dlm_rsb`)
- callbacks (`dlm_callback`)

Failures unwind already-created caches. `dlm_memory_exit()` calls `rcu_barrier()` before destroying caches so deferred frees have completed.

## Allocation Helpers
The file provides typed allocate/free wrappers for:
- RSBs and LKBs
- LVB buffers
- midcomms handles
- lowcomms writequeue entries
- lowcomms messages
- callbacks

RSBs and LKBs are freed with `call_rcu()`. RSB free releases `res_lvbptr`. LKB free releases user arguments and user LVB state for `DLM_DFL_USER_BIT` locks.

## Notes
Most allocation wrappers use `GFP_ATOMIC`, matching DLM use from spinlocked or recovery-sensitive contexts.
