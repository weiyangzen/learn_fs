<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c -->
# sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c

## Purpose
This file implements the top-level FSAL upcall vector used by NFS-Ganesha when a backend FSAL needs to notify the core server about lock availability, pNFS layout/device changes, delegation conflicts, and write-delegation attribute refreshes. It is the bridge from FSAL object handles and backend event keys into NFSv4 state, callback RPCs, delayed retry execution, and export/client lifetime management.

## Important APIs, Types, And Functions
- `struct fsal_up_vector fsal_up_top` is the exported template vector. FSAL exports copy it, set `up_fsal_export`/`up_gsh_export`, and optionally override operations.
- `lock_grant()` and `lock_avail()` rebuild an object handle from an FSAL handle and forward lock wakeups to `grant_blocked_lock_upcall()` or `available_blocked_lock_upcall()`.
- `layoutrecall()` validates a pNFS recall request, builds a `state_layout_recall_file`, sends per-client `CB_LAYOUTRECALL`, and uses `layoutrec_completion()` to retry or revoke/return layouts.
- `notify_device()` sends `CB_NOTIFY_DEVICEID` to all NFSv4.1 clients through `nfs41_foreach_client_callback()`.
- `delegrecall()` and helpers implement delegation recall, callback retry, and lease-time-based revocation.
- `cbgetattr_impl()` and helpers query a write-delegation holder for `CHANGE`/`SIZE` and update cached attributes.
- `up_ready_*()` functions provide readiness synchronization for upcall-capable modules.

## Control Flow
Layout recall converts the FSAL handle to an object, locks state, collects matching layout states by type/client/range, builds callback arguments, updates stateids, and schedules `layoutrecall_one_call()`. Completion accepts `NFS4_OK`, backs off for `NFS4ERR_DELAY`, treats `NFS4ERR_NOMATCHING_LAYOUT` as a return, and otherwise revokes/returns the layout through `nfs4_return_one_state()`.

Delegation recall scans object states under `STATELOCK`, marks `DELEG_GRANTED` as `DELEG_RECALL_WIP`, captures export/client refs, skips same-client lock-conflict cases, reserves the client lease, and sends `CB_RECALL`. Completion marks failed callback channels down, schedules retry or revoke checks, and revokes after lease-time thresholds.

`CB_GETATTR` transitions per-file state from `NONE` to `WIP`, reserves the client lease, sends callback getattr, and on success updates per-file modified/change/size fields and calls the upcall `update` hook.

## State And Persistence Behavior
State is in memory: object state lists, layout segment lists, delegation state fields, client refs, lease reservations, callback health, and per-file `cbgetattr` attributes. Durable effects are indirect through state revocation/return and FSAL update hooks.

## Dependencies And Integration Points
Integrates FSAL handle creation, SAL/NFSv4 state, pNFS helpers, NFS callback RPC, delayed execution, export lifecycle, server statistics, and MDCACHE-style update/invalidate overrides.

## Risks
- `create_file_recall()` appears to have an inverted overflow/range validation condition.
- Layout recall comments note possible reference leaks and incomplete revocation infrastructure.
- Delayed callbacks race with state/client/export teardown.
- `notify_device()` appears to leak the allocated foreach callback data.
- Top-vector invalidate/update operations are no-ops unless overridden.

## Test Signals
Cover delegation conflict, callback success/failure, expired clients, same-client lock suppression, pNFS recall selectors, delay retry, `NFS4ERR_NOMATCHING_LAYOUT`, revoke paths, and `CB_GETATTR` unchanged/changed/error cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL_UP/fsal_up_top.c -->
