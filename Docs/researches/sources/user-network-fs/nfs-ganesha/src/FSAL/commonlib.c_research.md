<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c

## Purpose

This large shared FSAL utility file implements common export/handle initialization, FSAL diagnostics, fsid encoding, ACL inheritance and mode conversion, remove/rename access helpers, share reservation accounting, file descriptor LRU and multi-FD synchronization, verifier helpers, referral detection, FSAL backend registration with the NFS service, and request operation-context lifecycle management.

## Important APIs, Types, and Functions

- Export/handle helpers: `fsal_attach_export`, `fsal_detach_export`, `fsal_export_init`, `fsal_export_stack`, `free_export_ops`, `fsal_default_obj_ops_init`, `fsal_obj_handle_init`, and `fsal_obj_handle_fini`.
- pNFS DS helpers: `fsal_pnfs_ds_init` and `fsal_pnfs_ds_fini`.
- Diagnostics/conversion: `msg_fsal_err`, `fsal_dir_result_str`, `display_fsinfo`, `display_attrlist`, `log_attrlist`, `encode_fsid`, and `decode_fsid`.
- ACL helpers: `fsal_inherit_acls`, `fsal_remove_access`, `fsal_rename_access`, `fsal_mode_to_acl`, `fsal_acl_to_mode`, and supporting static ACE generation/reuse helpers.
- Share helpers: `update_share_counters`, `check_share_conflict`, and `merge_share`.
- FD LRU globals and functions: `fsal_fd_mutex`, `fsal_fd_cond`, `fsal_fd_global_lru`, `fd_lru_state`, `lru_try_one`, `fd_lru_run`, `bump_fd_lru`, `insert_fd_lru`, `remove_fd_lru`, `fsal_init_fds_limit`, `fd_lru_pkginit`, and `fd_lru_pkgshutdown`.
- Multi-FD synchronization: `close_fsal_fd`, `reopen_fsal_fd`, `wait_to_start_io`, `fsal_start_global_io`, `fsal_start_io`, `fsal_complete_io`, `fsal_start_fd_work`, and `fsal_complete_fd_work`.
- Verifier/referral helpers: `set_common_verifier`, `check_verifier_stat`, `check_verifier_attrlist`, and `fsal_common_is_referral`.
- NFS service registration: `unregister_nfs_service_with_fsal_backend`, `fsal_registration_try_register`, and `register_nfs_service_with_fsal_backend`.
- Operation context: `init_ctx_refstr`, `destroy_ctx_refstr`, `set_op_context_export`, `set_op_context_client`, `set_op_context_pnfs_ds`, save/restore/discard helpers, `init_op_context`, `release_op_context`, `suspend_op_context`, and `resume_op_context`.
- Optional DBus summary: `fd_usage_summarize_dbus`.

## Control Flow

The early section provides direct initialization and list-management helpers. ACL functions either copy and transform inherited ACEs, synthesize ACLs from POSIX mode bits, derive POSIX mode from ACL order, or perform delete/rename access checks through object `test_access`. Share functions update counters and detect conflicts between access and deny modes.

The FD subsystem starts a fridge thread in `fd_lru_pkginit`. `fd_lru_run` waits for server initialization, monitors open FD counters against low/high/hard watermarks, reclaims global FDs from the LRU tail via `lru_try_one`, detects futility under high churn, and adjusts its next sleep interval based on FD count and open rate. I/O startup uses `wait_to_start_io` to coordinate `io_work`, `fd_work`, desired read/write flags, and reopen permissions. Reopen/close work waits for I/O quiescence, calls FSAL-specific reopen/close hooks, updates LRU membership/counters, and signals condition variables. `fsal_start_io` chooses state FD, related open-state/delegation FD, global FD, or temporary FD depending on state type, open flags, share reservations, and contention.

Operation-context functions manage thread-local `op_ctx`: initializing refs, switching exports/clients/pNFS DS contexts, saving/restoring nested export contexts, releasing refs, suspending async contexts, and resuming them.

## State and Persistence Behavior

Persistent process state includes FSAL registration lists protected by `fsal_registration_lock`, `nfs_service_ready`, global FD counters/LRU lists/state, LRU tuning parameters, the `no_export` refstr, and monotonic `op_id`. Object/export helpers manipulate FSAL export and handle intrusive lists. FD state persists in `struct fsal_fd` counters, open flags, condition variables, LRU links, and export pointers. Operation contexts hold references to exports, pNFS DS objects, and refcounted path strings until explicitly cleared or released.

## Dependencies and Integration Points

This file is central to the FSAL layer. It depends on Ganesha list, logging, config, NFS init, MDCACHE, NFSv4 ACL, state, pNFS, atomic, resource-limit, and optional DBus utilities. FSAL implementations call these helpers to initialize handles/exports, enforce common access semantics, manage FDs, and interact with request context. SAL/NFS request dispatch owns `op_ctx` setup and uses the save/restore helpers when crossing export boundaries.

## Risks and Edge Cases

- FD synchronization is complex: missed `io_work`/`fd_work` transitions or condition signals can deadlock I/O, reopen, close, or LRU reclamation.
- `reopen_fsal_fd` contains explicit stale `fsal_export` repair before LRU insertion; regressions here can cause use-after-free or wrong-export accounting after export reload.
- Global FD hard-limit behavior returns delay/temporary FD paths; tests need high-FD-pressure scenarios.
- ACL conversion must preserve delete/delete-child and inherited ACE semantics while updating mode-generated ACEs.
- `fsal_remove_access` intentionally treats `ERR_FSAL_NO_ACE` differently from explicit denial; changing that can alter NFSv4 delete semantics.
- Operation-context ref management must balance `get_gsh_export_ref`, `put_gsh_export`, `gsh_refstr_get/put`, and `pnfs_ds_get_ref/put`; leaks or double releases affect long-running servers.
- `fd_lru_pkgshutdown` converts any shutdown `rc`, including success, through `posix2fsal_error`; success depends on that mapper handling zero correctly.

## Test Signals

High-value tests include export stack setup/teardown, object handle list insertion/removal, fsid encode/decode variants, ACL inheritance/mode round trips, remove/rename access with `DELETE`, `DELETE_CHILD`, and no-ACE cases, share conflict and merge scenarios, FD LRU low/high/hard watermark behavior, concurrent read/write versus reopen/close, fallback to temp FD, stale export pointer repair after export reload, verifier set/check round trips, referral detection on sticky directories, NFS service registration before and after readiness, and op-context save/restore/release leak checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/commonlib.c -->
