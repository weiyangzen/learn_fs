<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/proto.h -->
# sources/user-network-fs/samba/source3/locking/proto.h

## Purpose
`proto.h` is the consolidated source3 locking prototype header for byte-range locks, general locking glue, POSIX lock mapping, and lease utility helpers. It exposes the cross-file API used by smbd locking callers.

## Important APIs, Types, And Functions
The header declares `brlock.c` APIs for initialization, range validation/overlap, lock/unlock/query/test, durable disconnect/reconnect, traversal, locked share-mode-plus-brlock callbacks, and lock snapshots. It declares `locking.c` APIs for strict-lock checks, request wrappers, close cleanup, share-mode formatting, rename, delete-on-close, stale entry, and lease traversal helpers. It declares `posix.c` APIs for kernel-lock checking, init/end, close handling, and Windows/POSIX flavour lock mapping. It declares lease utility functions `map_oplock_to_lease_type`, `fsp_lease_type`, and `fsp_client_guid`.

## Control Flow
The header defines callback contracts such as `share_mode_do_locked_brl_fn_t`, which receives a share-mode lock plus an optional byte-range lock snapshot. It lets higher-level code choose read-only or write paths by selecting `brl_get_locks_readonly`, `brl_get_locks`, or `share_mode_do_locked_brl`.

## State And Persistence
No state is stored in this header. It describes operations that mutate `locking.tdb`, `brlock.tdb`, `leases.tdb`, in-memory POSIX pending-close state, and per-`files_struct` caches.

## Dependencies And Integration Points
It includes `<tdb.h>` and relies on broad Samba declarations for `files_struct`, `share_mode_lock`, `lock_struct`, `server_id`, `file_id`, GUIDs, SMB2 lease keys, security tokens, NTSTATUS, and locking enums. It is the integration layer between source3 smbd request code and the individual locking implementation files.

## Risks And Test Signals
Because many types are only forward-declared elsewhere, include-order regressions are possible. The broad header also couples independent locking subsystems, so signature changes ripple widely. Test signals are full source3 builds, compile coverage of every prototype, and ABI/API checks for VFS modules or callers using byte-range and share-mode hooks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/proto.h -->
