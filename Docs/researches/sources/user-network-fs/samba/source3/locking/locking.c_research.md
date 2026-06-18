<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/locking.c -->
# sources/user-network-fs/samba/source3/locking/locking.c

## Purpose
`locking.c` is the request-facing glue for Samba source3 locking. It wraps byte-range lock operations, strict-lock checks, close-time cleanup, share-mode rename handling, delete-on-close token management, stale share/lease cleanup, and share-mode traversal helpers.

## Important APIs, Types, And Functions
Public functions include `lock_type_name`, `lock_flav_name`, `init_strict_lock_struct`, `strict_lock_check_default`, `query_lock`, `do_lock`, `do_unlock`, `locking_close_file`, `share_mode_str`, `rename_share_filename`, `get_file_infos`, `is_valid_share_mode_entry`, `share_entry_stale_pid`, `remove_lease_if_stale`, `get_delete_on_close_token`, `reset_delete_on_close_lck`, `set_delete_on_close_lck`, `set_delete_on_close`, `is_delete_on_close_set`, `file_has_open_streams`, and `share_mode_forall_leases`. Helper state structs bind callbacks to share-mode traversal and messaging.

## Control Flow
I/O strict locking builds a `lock_struct`, checks configuration and handle capability, optionally bypasses checks under `Auto` strict locking when the handle has a matching SMB2 lease, then tests `brlock.tdb` read-only. On conflict it retries under `share_mode_do_locked_brl` so dead lock owners can be cleaned. Lock/unlock request wrappers validate directories and non-lockable handles, call `brl_lock`/`brl_unlock`, and maintain `fsp->current_lock_count` as a fast close-time heuristic. Rename updates the share-mode record's service/base/stream names, sends `MSG_SMB_FILE_RENAME` to other openers, and updates each unique lease record. Delete-on-close stores security tokens by `name_hash` in `share_mode_data` and notifies peers to cancel deleted notifications.

## State And Persistence
This file mutates `brlock.tdb` indirectly through `brlock.c`, `locking.tdb` through `share_mode_lock.c`, and `leases.tdb` through `leases_db.c`. It also updates per-handle state such as `current_lock_count`, `delete_on_close`, share entry flags, name hashes, and cached lease type. Delete-on-close state is persisted inside share-mode data as token arrays keyed by name hash.

## Dependencies And Integration Points
It integrates the SMB request layer with byte-range locks, share-mode locks, messaging, server-id liveness, generated NDR rename/file-id blobs, security token duplication, SMB2 leases, and stream/base-open flags. It is used by open, read/write, rename, close, durable handle, and stream handling paths.

## Risks And Test Signals
Correctness depends on lock-count heuristics staying synchronized with actual lock records; POSIX-flavour locks intentionally disable exact counting with `NO_LOCKING_COUNT`. Rename notification and lease rename failures are mostly logged, so stale path metadata can persist after partial failure. Delete-token arrays use swap deletion, and repeated entries for a name hash need coverage. Stale pid marking modifies entries during validation. Test signals include strict-locking off/on/Auto, lease bypasses, close with pending locks, rename with multiple openers and hardlink name hashes, delete-on-close token replacement/reset, stale pid cleanup, stream-base-open detection, and SMB1 deny-mode flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/locking.c -->
