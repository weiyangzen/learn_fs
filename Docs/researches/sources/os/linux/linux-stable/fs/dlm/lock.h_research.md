# File Research: sources/os/linux/linux-stable/fs/dlm/lock.h

## Purpose
`lock.h` declares the public-internal lock engine API used by other DLM files.

## Exported Areas
- Debug/dump helpers: `dlm_dump_rsb()`, `dlm_dump_rsb_name()`, `dlm_print_lkb()`.
- Receive entry points: `dlm_receive_message_saved()`, `dlm_receive_buffer()`.
- Compatibility and lifetime: `dlm_modes_compat()`, `free_inactive_rsb()`, `dlm_put_rsb()`, `dlm_hold_rsb()`, `dlm_put_lkb()`.
- Recovery locking and timers: `dlm_lock_recovery_try()`, `dlm_lock_recovery()`, `dlm_unlock_recovery()`, `dlm_rsb_scan()`, `resume_scan_timer()`.
- Directory/master helpers: `dlm_master_lookup()`, `dlm_search_rsb_tree()`.
- Recovery helpers: purge, grant, waiters pre/post, recover master/process copy.
- Userspace lock operations: request, convert, adopt orphan, unlock, cancel, purge, deadlock, clear process locks.
- Debug mutation helpers used by `debug_fs.c`.

## Inline Helpers
- `is_master(r)` treats `res_nodeid == 0` as locally mastered and warns if master is unknown.
- `lock_rsb()` / `unlock_rsb()` wrap `spin_lock_bh()` and `spin_unlock_bh()` for RSB protection.

## Integration
This is the main cross-file contract for `lock.c`. Recovery, directory, debugfs, requestqueue, RCOM, and user device code use these declarations rather than reaching into `lock.c` internals.
