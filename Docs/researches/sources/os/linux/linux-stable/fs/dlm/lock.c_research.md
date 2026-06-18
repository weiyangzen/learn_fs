# File Research: sources/os/linux/linux-stable/fs/dlm/lock.c

## Purpose
`lock.c` is the central DLM lock engine. It implements lock request/convert/unlock/cancel operations, local and remote message handling, RSB/LKB lifetime management, grant policy, recovery repair, userspace lock wrappers, orphan/purge handling, and debug injection helpers.

## Operation Model
The file documents and implements a four-stage flow:
1. Public API: `dlm_lock()` and `dlm_unlock()`.
2. RSB selection: `request_lock()`, `convert_lock()`, `unlock_lock()`, `cancel_lock()`.
3. Local-vs-remote dispatch: `_request_lock()`, `_convert_lock()`, `_unlock_lock()`, `_cancel_lock()`.
4. Master-side mutation: `do_request()`, `do_convert()`, `do_unlock()`, `do_cancel()`.

Remote sends cause the matching `receive_*()` function on the master node to run the same `do_*()` logic and send a reply.

## Resource and Lock Lifetime
RSBs are stored in `ls_rsbtbl` and mirrored on slow active/inactive lists for iteration. Active RSBs are refcounted; inactive RSBs are cached as toss-list entries and later removed by `dlm_rsb_scan()`. Directory-mode RSBs may remain inactive as directory records for remotely mastered resources.

Key functions:
- `find_rsb()` dispatches to directory or no-directory lookup.
- `find_rsb_dir()` handles local requests, remote requests, directory records, stale master mappings, inactive resurrection, and master lookup uncertainty.
- `find_rsb_nodir()` uses hash-selected node as direct master in no-directory mode.
- `deactivate_rsb()` moves unused RSBs inactive and schedules toss scanning when appropriate.
- `free_inactive_rsb()` asserts all queues/lists are empty before freeing.

LKBs are allocated in `ls_lkbxa` by `create_lkb()` / `_create_lkb()`, found by `find_lkb()`, and released by `dlm_put_lkb()` / `__put_lkb()`. Queue membership adds references; removing from queues drops them.

## Grant Policy
The compatibility matrix implements VMS-style DLM lock mode compatibility. `dlm_lvb_operations` defines whether an LVB is returned, written, invalidated, or untouched for mode transitions.

`can_be_granted()` wraps `_can_be_granted()` and handles:
- `DLM_LKF_EXPEDITE` for NL requests.
- Grant/convert/wait queue conflicts.
- QUECVT FIFO conversion semantics.
- NOORDER bypass.
- conversion deadlock detection.
- CONVDEADLK demotion to NL.
- ALTPR/ALTCW alternate grant modes.

`grant_pending_locks()` tries convert queue then wait queue, grants newly available locks, and sends BASTs to granted locks when blocked waiters remain.

## Messaging
Send helpers construct `struct dlm_message` through midcomms:
- operation sends: request, convert, unlock, cancel.
- async sends: grant, BAST.
- directory sends: lookup, remove.
- replies: request/convert/unlock/cancel/lookup reply.
- purge messages for userspace orphan cleanup.

`send_common()` adds an LKB to `ls_waiters` before sending messages expecting replies. It supports overlap handling where cancel/force-unlock may be issued while another remote operation is pending.

Receive handlers validate message direction and lock identity, locate/create RSBs and LKBs, apply flags/LVB data, run master-side operations, and send replies. `dlm_receive_buffer()` validates node ids, resolves lockspace by global id, and dispatches MSG vs RCOM under `ls_recv_active`.

When the lockspace is recovering, `dlm_receive_message()` queues normal messages on the requestqueue instead of processing immediately.

## Directory/Master Interaction
`set_master()` chooses an LKB target from the RSB master state. If the master is unknown, it sends a lookup to the directory node and places later LKBs on `res_lookup`. `confirm_master()` releases or advances the lookup queue after lookup/request outcomes.

`dlm_master_lookup()` is the directory-node authority for name-to-master mapping. It can create inactive directory records, repair mappings during recovery, and return `DLM_LU_MATCH` or `DLM_LU_ADD`.

## Recovery
Recovery paths include:
- `dlm_recover_waiters_pre()`: handles outstanding waiters before recovery by marking requests/lookups for resend and faking local unlock/cancel replies when the peer is gone.
- `dlm_recover_waiters_post()`: clears waiter state, then resends or locally reprocesses affected requests/conversions, respecting overlap cancel/unlock flags.
- `dlm_recover_purge()`: removes master-copy locks for departed nodes and marks RSBs for grant/LVB recovery.
- `dlm_recover_grant()`: grants locks made possible by purging or rebuilt state.
- `dlm_recover_master_copy()` / `dlm_recover_process_copy()`: rebuild master-copy and process-copy lock state using RCOM lock records.

## Userspace Lock Path
Userspace wrappers mirror kernel APIs while attaching `struct dlm_user_args` and per-process ownership lists:
- `dlm_user_request()`
- `dlm_user_convert()`
- `dlm_user_adopt_orphan()`
- `dlm_user_unlock()`
- `dlm_user_cancel()`
- `dlm_user_deadlock()`
- `dlm_clear_proc_locks()`
- `dlm_user_purge()`

Persistent locks can become orphans and later be adopted by resource name/mode. Nonpersistent locks are force-unlocked on process cleanup. Purge can be local or sent remotely.

## Concurrency
Important synchronization includes:
- `ls_in_recovery` rwsem blocks normal locking during recovery.
- `res_lock` protects each RSB queue and core state.
- `ls_rsbtbl_lock` protects hash-table/list state.
- RCU protects lookup races while RSBs are removed from the hash table.
- `ls_lkbxa_lock` protects xarray/refcount transitions.
- `ls_waiters_lock`, `ls_orphans_lock`, and `ls_clear_proc_locks` protect auxiliary lists.
- Scan timer uses `ls_scan_lock` and avoids blocking recovery by checking `dlm_locking_stopped()`.

## Risks and Notes
This file is concurrency-sensitive and protocol-sensitive. The most fragile areas are waiter overlap handling, RSB inactive resurrection/removal races, directory/master uncertainty, and recovery resends. The code contains detailed comments explaining expected races, especially lookup/request optimization, remove-vs-request races, and aborted recovery cycles.
