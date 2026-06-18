# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_srv_deleg.c

Implements NFSv4 server delegation policy, callback-channel management, CB_RECALL and CB_GETATTR callbacks, v4.1 back-channel slot use, delegation grant/recall/revoke/return lifecycle, and cross-version delegation conflict checks.

Key elements:
- Delegation policy controls: `rfs4_set_deleg_policy()`, `rfs4_hold_deleg_policy()`, `rfs4_rele_deleg_policy()`, and `nfs4_get_deleg_policy()` protect or expose `nfs4_deleg_policy`; `rfs4_disable_delegation()` and `rfs4_enable_delegation()` maintain a temporary disable counter.
- Callback address handling:
  - `uaddr2sockaddr()` converts NFS universal addresses into IPv4/IPv6 socket addresses and ports.
  - `rfs4_client_setcb()` stores new v4.0 callback location/program/ident data, freeing previous pending data.
  - `rfs4_deleg_cb_check()` marks callback data confirmed and starts a `CB_NULL` tester thread.
  - `rfs4_cbinfo_free()` releases current and pending callback strings and cached callback clients.
- v4.0 callback path:
  - `rfs4_do_cb_null()` serializes callback path probing, promotes confirmed pending callback data, flushes stale clients, sends `CB_NULL`, and updates `CB_OK`, `CB_BAD`, or `CB_INPROG` state.
  - `rfs4_cbinfo_hold()` waits for callback setup and increments callback-info reference count only when the path is usable.
  - `rfs4_cbinfo_rele()` releases callback-info references, marks failures, wakes waiters, and signals when new callback data should be retried.
  - `rfs4_cbch_init()`, `rfs4_cb_getch()`, `rfs4_cb_freech()`, and `rfs4_cb_chflush()` create, cache, reset, and destroy RPC client handles for callback RPCs.
- General callback execution: `rfs4_do_callback()` sends v4.0 `CB_COMPOUND` calls with callback-info hold/release semantics and retries if a failed call races with newly confirmed callback data.
- Callback argument/result cleanup: `rfs4args_cb_recall_free()`, `rfs4args_cb_getattr_free()`, `rfs41args_cb_sequence_free()`, and `rfs4freeargres()` free nested filehandles, referring-call lists, tags, arg arrays, and XDR-decoded results.
- v4.1 back-channel support:
  - `svc_slot_maxslot()`, `svc_slot_alloc()`, `svc_slot_free()`, and `svc_slot_cb_seqid()` manage server-side use of the session back-channel slot table and sequence ids.
  - `rfs4x_cb_getch()`, `rfs4x_cb_freech()`, `rfs4x_cb_chflush()`, and `rfs4x_cb_chinit()` manage v4.1 callback RPC clients tied to the session back-channel and callback security parameters.
  - `rfs41_cb_seq_rcl_args()` builds a one-entry referring call list for callback sequence arguments when recallable state is still referenced.
- CB_RECALL:
  - `rfs4_do_cb_recall()` sends v4.0 `CB_RECALL` for a delegation stateid and filehandle, records recall time, and returns the delegation on callback failure.
  - `rfs4x_do_cb_recall()` sends v4.1 `CB_SEQUENCE + CB_RECALL`, uses back-channel slots, retries after lease delay for transport or delay errors, revokes on persistent failures, and updates callback sequence state.
- CB_GETATTR:
  - `rfs4_find_write_deleg_byfp()` and `rfs4_find_write_deleg()` locate a held write delegation on a file or vnode.
  - `rfs4_do_cb_getattr()` and `rfs4x_do_cb_getattr()` ask a write-delegation holder for `FATTR4_CHANGE` and `FATTR4_SIZE` and decode returned attrlists.
  - `rfs4_cb_getattr()` dispatches to v4.0 or v4.1 callback style and writes returned change/size values only when successfully decoded.
- Recall threading:
  - `rfs4_recall_file()` records recall timing/conflicting client and starts a master recall thread.
  - `do_recall_file()` walks a file's delegation list, holds each valid delegation, starts per-delegation recall threads, waits for recall count to drain, then releases the file.
  - `do_recall()` invokes the selected recall callback if the delegation still exists, decrements file recall count, releases the delegation, and exits.
  - `rfs4_recall_deleg()` throttles repeat recalls and revokes a file's delegations after lease-time recall and last-write thresholds.
- Delegation conflict and grant policy:
  - `rfs4_check_recall()` decides whether a conflicting open must recall an existing delegation, suppressing self-conflicts.
  - `rfs4_check_delegation()` chooses the best possible delegation type from current open share access/deny counts and current file delegation state.
  - `rfs4_delegation_policy()` applies server policy, recent recall/return history, conflicting-client tracking, and a read-delegation grant limit.
  - `rfs4_grant_delegation()` enforces policy, client request preferences, callback availability, lock-manager activity, remove/rename hold-off, recall delay state, CLAIM_PREVIOUS reclaim behavior, and then calls `rfs4_deleg_state()`.
- Delegation state installation:
  - `rfs4_deleg_state()` creates or finds a delegation state, temporarily drops locks to avoid deadlock, checks for races and conflicting opens/maps, installs vnode event monitors (`deleg_rdops` or `deleg_wrops`), upgrades vnode open counts, links the delegation to the file list, and updates grant counters/timestamps.
  - `rfs4_set_deleg_response()` fills the NFSv4 OPEN response delegation union and default deny ACE.
- Delegation conflict checks for other protocols:
  - `rfs4_check_delegated_byfp()` recalls delegations for v2/v3 or local file access conflicts, optionally delays for quick return, and holds off new grants for remove/rename.
  - `rfs4_check_delegated()` wraps the vnode-to-file lookup for NFSv2/v3 callers.
  - `rfs4_clear_dont_grant()` releases the remove/rename grant hold.
- Delegation return and revocation:
  - `rfs4_return_deleg()` removes a delegation from the file list, cleans v4.1 recallable-state/session slot references, uninstalls monitors when the last delegation leaves, downgrades vnode open references, updates counters/timestamps, invalidates or marks state revoked, and increments the client's revoked-delegation count for v4.1 SEQUENCE status.
  - `rfs4_revoke_deleg()`, `rfs41_revoke_deleg()`, and `rfs4_revoke_file()` revoke one or all delegations while handling session presence.
- Miscellaneous helpers: `rfs4_vop_getattr()` maps `VOP_GETATTR()` errors to NFSv4 status, `rfs4_delegated_getattr()` currently forwards to `VOP_GETATTR()`, `rfs41_file_still_delegated()` checks file delegation liveness, `rfs4_is_deleg()` detects delegation ownership by another client, and `rfs4_mon_hold()`/`rfs4_mon_rele()` manage file holds for vnode monitors.

Dependencies:
- NFSv4 state model: `rfs4_client_t`, `rfs4_session_t`, `rfs4_state_t`, `rfs4_file_t`, `rfs4_deleg_state_t`, `rfs4_dbe_*`, `rfs4_findfile()`, `rfs4_finddeleg()`, `rfs4_deleg_state_rele()`.
- RPC/back-channel APIs: `CLIENT`, `clnt_call`, `clnt_tli_kcreate`, `CLNT_CONTROL`, `AUTH_DESTROY`, `authnone_create`, `xdr_CB_COMPOUND4args_srv`, `xdr_CB_COMPOUND4res`.
- Session/slot helpers: `SN_CB_CHAN_EST`, `SNTOBC`, `CTOBSD`, `slot_alloc`, `slot_free`, `slot_table_query`, `slot_incr_seq`, `rfs4x_findsession_by_clid`, `rfs4x_findsession_by_id`, `rfs4x_session_rele`, `rfs4x_rs_erase`.
- Kernel synchronization/threading: mutexes, rwlocks, CVs, `zthread_create`, `zthread_exit`, CPR callbacks, `delay()`, lease-time calculations.
- Vnode and file monitoring: `VOP_GETATTR`, `vnevent_support`, `fem_install`, `fem_uninstall`, `vn_open_upgrade`, `vn_open_downgrade`, `vn_is_opened`, `vn_has_other_opens`, `vn_is_mapped`.
- Lock manager and transport helpers: `lm_vp_active`, `lookupname`, `inet_pton`, `svc_getrpccaller`, callback security helpers.

Research notes:
- The file carefully avoids holding file/state locks across network callbacks; recall work is handed to threads with explicit dbe holds.
- v4.0 and v4.1 callback paths are intentionally separate: v4.0 uses client-supplied callback address strings, while v4.1 uses the session back-channel and slot sequencing.
- `rfs4_return_deleg()` has different revoked-state behavior for v4.0 versus v4.1. v4.0 closes/reaps state, while v4.1 keeps revoked state until FREE_STATEID or client cleanup so SEQUENCE status can report revoked recallable state.
- Delegation grants depend on both protocol-level share state and local vnode open/map state; monitor installation is bracketed by conflict checks to reduce races.
- `rfs4_delegated_getattr()` is currently only a wrapper, but CB_GETATTR support in this file gives the v4 server a path to ask write-delegation holders for authoritative change/size values.
