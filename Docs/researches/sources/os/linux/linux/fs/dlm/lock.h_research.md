# File Research: sources/os/linux/linux/fs/dlm/lock.h

## Role

`lock.h` declares the internal interfaces exported by `lock.c` to the rest of the DLM implementation. It also defines the fundamental RSB locking helpers used by debug, recovery, directory, and lockspace code.

## Exported Areas

The declarations cover:

- Debug/dump helpers: `dlm_dump_rsb()`, `dlm_dump_rsb_name()`, `dlm_print_lkb()`.
- Receive entry points: `dlm_receive_buffer()`, `dlm_receive_message_saved()`.
- Compatibility: `dlm_modes_compat()`.
- RSB/LKB lifetime: `free_inactive_rsb()`, `dlm_hold_rsb()`, `dlm_put_rsb()`, `dlm_put_lkb()`.
- Recovery gating: `dlm_lock_recovery()`, `dlm_unlock_recovery()`, `dlm_lock_recovery_try()`.
- Inactive RSB scan timer: `dlm_rsb_scan()`, `resume_scan_timer()`.
- Directory/master lookup helpers: `dlm_master_lookup()`, `dlm_search_rsb_tree()`.
- Recovery lock reconstruction and grant paths.
- Userspace DLM operations and process cleanup.
- Debug LKB/waiter insertion helpers.

## Inline Helpers

`is_master(struct dlm_rsb *r)` returns true when `res_nodeid` is zero and warns if `res_nodeid == -1`, because unknown master state should not be tested as master state.

`lock_rsb()` and `unlock_rsb()` wrap `spin_lock_bh()` and `spin_unlock_bh()` around `r->res_lock`. These helpers encode the DLM convention that RSB queue/state mutations run with bottom halves disabled.

## Research Notes

The header is intentionally broad because `lock.c` owns much of the subsystem's shared behavior. For new readers, `lock.h` is a useful map of which pieces outside `lock.c` are allowed to touch lock state directly.
