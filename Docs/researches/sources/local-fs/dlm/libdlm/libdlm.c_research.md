# File Research: sources/local-fs/dlm/libdlm/libdlm.c

## Purpose
Implements the user-space `libdlm` API over the Linux kernel DLM misc-device ABI.

## Main Responsibilities
- Open/create/release DLM lockspaces via `/dev/misc/dlm-control`.
- Open per-lockspace misc devices under `/dev/misc/dlm_<name>`.
- Encode lock/unlock/purge/deadlock requests into kernel ABI write requests.
- Read AST/BAST completion records from the lockspace fd and invoke user callbacks.
- Provide synchronous wrappers using `LKF_WAIT`.
- Provide optional pthread receiver threads for asynchronous callbacks.

## ABI Handling
- Supports kernel DLM device ABI v5 through local `dlm_write_request_v5` and result structs.
- Supports v6+ through kernel `struct dlm_write_request` and `struct dlm_lock_result`.
- Detects kernel ABI version by reading `dlm-control`; falls back to version 5 if read fails.
- Marks request architecture width through `is64bit`.

## Key APIs Implemented
- Default lockspace: `dlm_lock`, `dlm_unlock`, `dlm_lock_wait`, `dlm_unlock_wait`, `dlm_get_fd`, `dlm_dispatch`.
- Named lockspaces: `dlm_create_lockspace`, `dlm_new_lockspace`, `dlm_open_lockspace`, `dlm_close_lockspace`, `dlm_release_lockspace`, `dlm_ls_get_fd`.
- Named lockspace locking: `dlm_ls_lock`, `dlm_ls_lockx`, `dlm_ls_lock_wait`, `dlm_ls_unlock`, `dlm_ls_unlock_wait`.
- Maintenance: `dlm_ls_deadlock_cancel`, `dlm_ls_purge`, version queries.
- Threaded-only helpers: `lock_resource`, `unlock_resource`, `dlm_pthread_init`, `dlm_ls_pthread_init`, `dlm_pthread_cleanup`.

## Notable Design
- `default_ls` is global and intentionally not heavily synchronized; callers are expected to coordinate.
- Synchronous writes either block on a condition variable or, when already in the AST thread, dispatch completions until `sb_status` changes.
- Lockspace creation waits for udev to create the device and handles truncated sysfs names by adding a symlink.
- `dlm_release_lockspace()` closes/cancels pthread handling before asking the kernel to remove the lockspace.

## Risks / Gaps
- Range locks are explicitly unsupported and return `ENOSYS`.
- `timeout` passed to `dlm_ls_lockx()` is accepted in the API but not copied into the v6 request in this implementation.
- Some pthread condition waits are not wrapped in predicate loops, so spurious wakeups are theoretically possible.
- Global `control_fd`, `default_ls`, and version state are not fully thread-safe.
