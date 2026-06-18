<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.h -->
# sources/user-network-fs/samba/source3/locking/share_mode_lock.h

## Purpose
`share_mode_lock.h` exposes the public share-mode lock API for source3 code. It defines initialization, locked and unlocked record access, entry mutation, traversal, async fetch/watch, share-mode flags, and prepare-lock helpers while keeping `struct share_mode_lock` and `struct share_mode_data` opaque to most callers.

## Important APIs, Types, And Functions
The header declares `locking_init`, `locking_init_readonly`, `locking_end`, `share_mode_lock_file_id`, `get_existing_share_mode_lock`, `set_share_mode`, `del_share_mode`, `del_share_mode_open_id`, `reset_share_mode_entry`, `mark_share_mode_disconnected`, `remove_share_oplock`, `downgrade_share_oplock`, `file_has_read_lease`, `fetch_share_mode_unlocked`, async `fetch_share_mode_send/recv`, traversal functions, `share_mode_count_entries`, `share_mode_flags_get/set`, `share_mode_watch_send/recv`, `share_mode_wakeup_waiters`, VFS-allowed/denied locked callback wrappers, and prepare-lock/unlock macros. `struct share_mode_entry_prepare_state` embeds enough private storage for an in-place `share_mode_lock`.

## Control Flow
Callers generally acquire a locked record with `get_existing_share_mode_lock` or through callback helpers, mutate entries or data, and rely on talloc/destructor or explicit helper completion to store and unlock. The prepare-lock macros support open paths that may keep the share-mode lock across a staged operation and later release it through `share_mode_entry_prepare_unlock`.

## State And Persistence
The header owns no state, but its contracts govern mutation of `locking.tdb` records and watcher state. The embedded prepare-state union fixes an ABI-like space requirement for the private lock object.

## Dependencies And Integration Points
It includes tevent, file-id, time, and NTSTATUS headers, and forward-declares smbd structures. It is consumed by locking glue, open/close handling, durable handle code, status reporting, oplock/lease paths, and VFS-sensitive code that must distinguish callbacks allowed to call blocking VFS operations from callbacks that must not.

## Risks And Test Signals
The prepare-state storage size must remain large enough for the private `struct share_mode_lock`; the implementation asserts this at runtime. The macros inject `__location__`, so include context matters. Misusing VFS-denied callbacks for blocking operations risks lock stalls. Test signals include compile coverage of all callers, prepare-lock keep/release paths, async fetch/watch API use, and assertions for share entry flags restored during durable reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.h -->
