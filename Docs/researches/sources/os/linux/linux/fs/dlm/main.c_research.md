# File Research: sources/os/linux/linux/fs/dlm/main.c

## Role

`main.c` is the DLM module entry/exit file. It wires initialization and cleanup ordering for memory caches, communication, lockspaces, configfs/debugfs, user devices, plock support, and the DLM workqueue.

## Initialization Flow

`init_dlm()` runs:
1. `dlm_memory_init()`
2. `dlm_midcomms_init()`
3. `dlm_lockspace_init()`
4. `dlm_config_init()`
5. `dlm_register_debugfs()`
6. `dlm_user_init()`
7. `dlm_plock_init()`
8. `alloc_workqueue("dlm_wq", WQ_PERCPU, 0)`

Failures unwind in reverse order for already initialized components.

## Exit Flow

`exit_dlm()` destroys `dlm_wq`, exits plock/user/config/lockspace/midcomms, unregisters debugfs, and destroys memory caches.

## Exports

The module exports `dlm_new_lockspace`, `dlm_release_lockspace`, `dlm_lock`, and `dlm_unlock`.

## Important Behaviors and Invariants

The shared `dlm_wq` must be destroyed before subsystem exit so pending freeing or callback work is complete. Midcomms initialization happens before lockspace/config use, but actual lowcomms socket startup is controlled later by lockspace/config paths.

## Research Notes

Read completely. This file defines module-level ordering rather than lock protocol logic.
