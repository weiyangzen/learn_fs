# File Research: sources/os/linux/linux/fs/dlm/lock.c

## Role

`lock.c` is the central DLM lock manager implementation. It owns the lock/request state machine, RSB and LKB lookup/lifetime, lock compatibility rules, LVB propagation, inter-node DLM message send/receive, recovery reconciliation, userspace lock operations, orphan/purge handling, and debug injection helpers.

## High-Level Locking Pipeline

The file documents four stages:

1. Public API split:
   - `dlm_lock()` handles request or convert.
   - `dlm_unlock()` handles unlock or cancel.
2. Stage 2 finds and locks the relevant RSB:
   - `request_lock()`, `convert_lock()`, `unlock_lock()`, `cancel_lock()`.
3. Stage 3 decides local vs remote:
   - `_request_lock()`, `_convert_lock()`, `_unlock_lock()`, `_cancel_lock()`.
4. Stage 4 mutates the master-side queues:
   - `do_request()`, `do_convert()`, `do_unlock()`, `do_cancel()`.

Remote operations call `send_*()`, which causes the peer's `receive_*()` path to run the same stage-4 logic on the master node and return a reply.

## Compatibility and LVB Rules

The file defines:

- The VMS-style lock-mode compatibility matrix for `NL`, `CR`, `CW`, `PR`, `PW`, and `EX`.
- `dlm_modes_compat()` as the exported mode compatibility helper.
- `dlm_lvb_operations`, which determines whether a lock transition reads the resource LVB, writes/invalidates it, or leaves it untouched.
- A separate QUECVT compatibility matrix for conversion queuing.

`set_lvb_lock()`, `set_lvb_unlock()`, and `set_lvb_lock_pc()` implement master/local/process-copy LVB transfer and invalidation. The code increments `res_lvbseq` when the resource LVB is updated and propagates invalid-state flags through `DLM_SBF_VALNOTVALID`.

## RSB Lifetime and Resource Table

RSBs live in `ls_rsbtbl` and on slow active/inactive lists:

- Active RSBs are refcounted and on `ls_slow_active`.
- Inactive RSBs are not refcounted and are on `ls_slow_inactive`.
- `RSB_HASHED` records rhashtable membership.
- `RSB_INACTIVE` records inactive/toss-list state.

`find_rsb()` computes the resource hash, maps it to a directory node with `dlm_hash2nodeid()`, enters an RCU read-side section, and dispatches to `find_rsb_dir()` or `find_rsb_nodir()`.

`find_rsb_dir()` handles the normal directory-enabled model, including:

- Local requests.
- Requests received from the directory node.
- Requests received from other nodes.
- Inactive RSB reuse.
- stale master detection via `RSB_MASTER_UNCERTAIN`.
- Directory records for remote masters.

`find_rsb_nodir()` handles no-directory mode by treating the hash-selected directory node as the master and allowing recovery-time remote master copies to arrive before local recovery has finished promoting the RSB.

`deactivate_rsb()` moves an RSB to inactive state when its refcount reaches zero, decides whether it must remain as a directory record, and schedules toss cleanup through `add_scan()`. `dlm_rsb_scan()` periodically frees expired inactive RSBs and sends `DLM_MSG_REMOVE` to the directory node when a local master/non-directory record is discarded.

## LKB Lifetime and Queues

LKBs are allocated in `ls_lkbxa` through `create_lkb()`/`_create_lkb()` and looked up with `find_lkb()`. `__put_lkb()` removes the LKB from the xarray at final refcount drop, detaches its RSB, frees master-copy LVB storage, and frees the LKB.

Within an RSB:

- `add_lkb()` places an LKB on the grant, convert, or wait queue and records a timestamp.
- `del_lkb()` removes it and drops the queue reference.
- `move_lkb()` switches queues.
- Grant queues are kept ordered by granted mode.

The file distinguishes queue mutations for master/local copies from process-copy updates using variants such as `grant_lock_pc()`, `remove_lock_pc()`, and `revert_lock_pc()`.

## Granting and Blocking ASTs

`can_be_granted()` wraps `_can_be_granted()` with special handling for:

- `DLM_LKF_EXPEDITE` NL requests.
- Conversion deadlock detection.
- `DLM_LKF_CONVDEADLK` demotion to NL.
- `DLM_LKF_ALTPR`/`DLM_LKF_ALTCW` alternate-mode grants.
- `DLM_LKF_QUECVT`, `DLM_LKF_NOORDER`, and normal FIFO conversion/wait ordering.

`grant_pending_locks()` first grants eligible conversions, then eligible waiters, then sends BAST callbacks to granted locks that block the highest remaining request. Special PR/CW middle-mode behavior is handled to request EX-level blocking when needed.

`queue_cast()` and `queue_bast()` send completion/blocking callbacks locally via `dlm_add_cb()` or remotely through `send_grant()`/`send_bast()` for master copies.

## Master Lookup and Directory Interaction

`set_master()` ensures `lkb_nodeid` is set before a request proceeds:

- If the master is known local, it sets nodeid 0.
- If known remote, it copies the remote nodeid.
- If unknown and this node is the directory owner, it promotes local master state.
- Otherwise it sends a lookup and queues the initiating LKB as the first lookup waiter.

`process_lookup_list()` retries LKBs queued behind the initial lookup. `confirm_master()` resolves or advances the `res_first_lkid` lookup gate depending on success or errors.

`dlm_master_lookup()` is the directory-side implementation used by normal lookup messages and recovery. It can create inactive directory records, update master mappings during recovery, and return whether the record matched or was newly added.

## Public Kernel API

`dlm_lock()`:

- Locates the lockspace.
- Takes the recovery read lock.
- Creates or finds an LKB.
- Validates and stores lock args.
- Executes request or convert.
- Normalizes `-EINPROGRESS`, `-EAGAIN`, and `-EDEADLK` into API-level success when the completion is reported through AST semantics.

`dlm_unlock()`:

- Locates the lockspace.
- Takes the recovery read lock.
- Finds the LKB.
- Validates unlock/cancel flags.
- Executes cancel or unlock.
- Normalizes DLM completion statuses and allowed `-EBUSY` overlap cases.

Both functions trace start/end events and release lockspace/LKB references on exit.

## Wire Message Send Path

`create_message()` sizes messages by type, including resource names or LVB payloads where required. `_create_message()` fills the common DLM header and obtains a midcomms message handle.

`send_common()` adds the LKB to the waiters list, creates a message, serializes common LKB fields with `send_args()`, and commits it through `dlm_midcomms_commit_mhandle()`. On send setup failure it removes the waiter state.

Special send paths include:

- `send_convert()`, which locally synthesizes a convert reply for down-conversions because the master does not reply.
- `send_lookup()`, which targets the directory node and waits for `DLM_MSG_LOOKUP_REPLY`.
- `send_remove()`, which tells a directory node to delete an inactive record.
- `send_purge()`, which remotely purges user orphan locks.

## Receive Path

`dlm_receive_buffer()` validates the packet sender, finds the lockspace by global id, takes `ls_recv_active`, and dispatches either normal messages or RCOM recovery messages.

Normal messages enter `dlm_receive_message()`:

- If receive processing is blocked for recovery, messages are saved to `ls_requestqueue`.
- Otherwise `_receive_message()` dispatches by DLM message type.

Receive handlers include:

- `receive_request()`: creates a master-copy LKB, finds/validates the RSB, runs `do_request()`, sends request reply, then applies request effects.
- `receive_convert()`, `receive_unlock()`, `receive_cancel()`: find the master-copy LKB, validate source/type, apply args, run stage-4 logic, reply, and apply effects.
- `receive_grant()` and `receive_bast()`: apply asynchronous master-to-process notifications.
- `receive_lookup()`: runs directory lookup and optimizes lookup-to-request when this node is also the master.
- `receive_remove()`: removes inactive directory records, while ignoring expected races against active local use.
- Reply handlers update waiter state, process-copy queue state, LVBs, alternate/demoted modes, overlap unlock/cancel state, and lookup confirmation.

`validate_message()` enforces expected process-copy/master-copy direction and prevents mixing user and kernel lock messages.

## Waiters and Overlap Handling

Remote operations place LKBs on `ls_waiters` with `add_to_waiters()`. The code supports overlapping force-unlock/cancel while an operation is already waiting:

- `DLM_IFL_OVERLAP_UNLOCK_BIT`
- `DLM_IFL_OVERLAP_CANCEL_BIT`
- `lkb_wait_count` for multiple expected replies

`_remove_from_waiters()` handles normal and overlapping replies, including a special case where a successful convert reply preemptively clears an outstanding cancel overlap so the application is not blocked by stale state.

## Recovery Integration

`dlm_recover_waiters_pre()` walks waiters before recovery:

- Lookup waiters are marked for resend.
- Requests and up-conversions to failed/changing masters are marked for resend.
- Unlocks, cancels, and some down-conversions are completed with local synthetic replies.

`dlm_recover_waiters_post()` reprocesses waiters marked `DLM_IFL_RESEND_BIT` after recovery. It forcibly clears previous waiter state, handles overlapping unlock/cancel if present, then reruns `_request_lock()` or `_convert_lock()` so operations use the new master mapping.

`dlm_recover_master_copy()` receives lock records from old process owners and reconstructs master-copy LKBs on the new master. It deduplicates by remote nodeid/remid and sets `RSB_RECOVER_GRANT` when recovered queues may now be grantable.

`dlm_recover_process_copy()` processes replies for sent recovery locks, updates process-copy remote ids, resends on `-EBADR`, and acknowledges recovered locks with `dlm_recovered_lock()`.

`dlm_recover_purge()` removes master-copy locks belonging to departed nodes and marks LVBs invalid when departed holders had PW/EX VALBLK locks.

`dlm_recover_grant()` scans resources marked `RSB_RECOVER_GRANT`, runs `grant_pending_locks()`, clears the flag, and confirms master state.

## Userspace DLM Operations

The userspace-facing wrappers mirror kernel operations while managing `struct dlm_user_args` and per-process lists:

- `dlm_user_request()`
- `dlm_user_convert()`
- `dlm_user_unlock()`
- `dlm_user_cancel()`
- `dlm_user_deadlock()`
- `dlm_user_adopt_orphan()`
- `dlm_user_purge()`
- `dlm_clear_proc_locks()`

Userspace locks set `DLM_DFL_USER_BIT`, use fake kernel callbacks internally, keep user callback/lksb pointers in `dlm_user_args`, and are moved among process `locks`, `unlocking`, `asts`, and lockspace `orphans` lists. Persistent user locks can become orphan locks and later be adopted by matching resource name and mode.

## Debug Helpers

`dlm_debug_add_lkb()` creates a synthetic non-user LKB with a caller-chosen id, attaches it to an RSB found by name, and inserts it onto the requested status queue. `dlm_debug_add_lkb_to_waiters()` finds an existing LKB and adds waiter state. These are used by `debug_fs.c` write handlers.

## Dependencies

`lock.c` depends on nearly every DLM subsystem: memory allocation, midcomms, requestqueue, directory, membership, lockspace lifetime, AST callbacks, recovery communication, LVB tables, userspace device support, config, and tracepoints.

## Research Notes

This file is the behavioral heart of DLM. The critical invariants are:

- RSB queue membership is protected by `res_lock`.
- RSB table/list membership is protected by `ls_rsbtbl_lock` and RCU during lookup/reuse races.
- LKB id lookup and final removal are protected by `ls_lkbxa_lock`.
- Normal locking is gated by `ls_in_recovery`.
- Remote operations must be represented on `ls_waiters` until a real or synthetic reply resolves them.
- Recovery can invalidate master mappings, requiring resend/replay of pending operations rather than simply failing user-visible requests.
