# File Research: sources/os/linux/linux/fs/dlm/memory.c

## Role

`memory.c` centralizes DLM object allocation through slab caches and RCU-delayed frees.

## Cache Lifecycle

`dlm_memory_init()` creates caches for:
- lowcomms write queue entries
- midcomms message handles
- lowcomms messages
- lock blocks (`dlm_lkb`)
- resource blocks (`dlm_rsb`)
- callbacks (`dlm_callback`)

Failure unwinds already created caches. `dlm_memory_exit()` calls `rcu_barrier()` before destroying caches so deferred frees are complete.

## Allocation Helpers

The file provides typed allocate/free wrappers for RSBs, LKBs, LVB buffers, message handles, writequeue entries, messages, and callbacks.

RSBs and LKBs are freed through `call_rcu()`. RSB release frees its LVB pointer. LKB release frees user-argument state and user LVB memory when the lock belongs to the user API.

## Important Behaviors and Invariants

- Most allocations use `GFP_ATOMIC`, reflecting DLM use from spinlocked or recovery-sensitive contexts.
- Cache destruction relies on `rcu_barrier()` to avoid freeing slabs before callbacks have run.
- User LKB cleanup must release embedded user state only for `DLM_DFL_USER_BIT` locks.

## Research Notes

Read completely. This is infrastructure code with no protocol control flow, but it defines lifetime assumptions used across the DLM subsystem.
