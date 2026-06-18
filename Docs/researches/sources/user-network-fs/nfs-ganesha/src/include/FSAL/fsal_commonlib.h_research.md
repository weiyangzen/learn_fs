<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h

## Purpose
`FSAL/fsal_commonlib.h` declares common FSAL support routines for module registration, export and object-handle lifecycle, pNFS data-server state, ACL inheritance/conversion, share reservation management, fd lifecycle, verifier handling, referral detection, and export updates.

## Important APIs, types, and functions
- `fsal_registration_entry_t` tracks FSAL modules that need NFS service backend registration.
- Registration APIs include `fsal_registration_try_register()`, `unregister_nfs_service_with_fsal_backend()`, and `register_nfs_service_with_fsal_backend()`.
- Export/object lifecycle APIs include `fsal_attach_export()`, `fsal_detach_export()`, `fsal_export_init()`, `fsal_export_stack()`, `free_export_ops()`, `fsal_default_obj_ops_init()`, `fsal_obj_handle_init()`, and `fsal_obj_handle_fini()`.
- `fsal_obj_handle_is()` is a type-test inline.
- pNFS helpers include `fsal_pnfs_ds_init()`, `fsal_pnfs_ds_fini()`, `encode_fsid()`, and `decode_fsid()`.
- ACL and access helpers include `fsal_inherit_acls()`, `fsal_remove_access()`, `fsal_rename_access()`, `fsal_can_reuse_mode_to_acl()`, `fsal_mode_to_acl()`, and `fsal_acl_to_mode()`.
- Share helpers include `update_share_counters()`, `check_share_conflict()`, `check_share_conflict_and_update()`, locked variants, and `merge_share()`.
- FD helpers include `fsal_close_fd()`, `fsal_reopen_fd()`, `close_fsal_fd()`, `fsal_start_global_io()`, `fsal_start_io()`, `fsal_complete_io()`, `fsal_start_fd_work()`, `fsal_complete_fd_work()`, and FD LRU helpers.
- `init_state()` initializes `state_t` and copies lock owner key data from related state when present.
- Verifier/referral/export APIs include `set_common_verifier()`, `check_verifier_stat()`, `check_verifier_attrlist()`, `fsal_common_is_referral()`, and `update_export()`.

## Control flow
FSAL modules initialize module and export state, attach exports to module lists, initialize object handles with default operation vectors, and use common helpers for operations that span modules. I/O paths use `fsal_start_io()` or `fsal_start_global_io()` to choose or open an fd while honoring share reservations, perform work, then call completion helpers to release fd work state and maintain LRU state. Share-conflict helpers check requested open flags and optionally update counters atomically under object locks.

## State and persistence
The header describes manipulation of persistent runtime objects: `fsal_module`, `fsal_export`, `fsal_obj_handle`, `fsal_share`, `fsal_fd`, `state_t`, and pNFS data-server state. State is in memory, but many helpers mirror or gate persistent filesystem operations. Locked variants mutate share counters under `obj_hdl->obj_lock`.

## Dependencies and integration points
It depends on `fsal_api.h`, `sal_data.h`, and `sal_functions.h`. It is a major integration point between FSAL modules, SAL state, NFS service registration, pNFS, NFSv4 share reservations, object-handle operations, fd caching, ACL mapping, and export reload/update code.

## Risks
- Share-reservation updates must stay atomic with conflict checks. Calling unlocked helpers without external locking can corrupt counters or allow conflicting opens.
- FD lifecycle is subtle: `fsal_start_io()` may reuse state fds, object fds, or temporary fds, and every successful start needs matching completion.
- `fsal_start_fd_work_no_reclaim()` treats failure as fatal; callers must only use it where failure is impossible by invariant.
- ACL mode conversion can lose information unless `fsal_can_reuse_mode_to_acl()` is respected.
- Export stacking and update paths can involve multiple modules; reference and operation-vector ownership must remain clear.

## Test signals
- FSAL common tests should cover object/export initialization/finalization, attach/detach lists, and default ops installation.
- Share tests should cover read/write/deny combinations, bypass behavior, locked and unlocked variants, and merge logic.
- FD tests should exercise open/reopen/close, global fd reuse, state fd reuse, LRU insert/bump/remove, reclaiming, and completion after errors.
- ACL tests should verify inheritance, mode-to-ACL and ACL-to-mode conversion, remove/rename access checks, and verifier truncation behavior.
- Export update tests should cover in-place update and stacked FSAL update cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_commonlib.h -->
