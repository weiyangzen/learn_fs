# File Research: sources/os/linux/linux/fs/ocfs2/dlm/dlmconvert.c

## Purpose
Implements lock conversion for OCFS2 DLM lock resources, covering both local-master conversion and remote conversion requests to the current resource master.

## Main Entry Points
- `dlmconvert_master()` handles conversion when the local node owns the lock resource.
- `dlmconvert_remote()` queues a local pending conversion and sends `DLM_CONVERT_LOCK_MSG` to the master.
- `dlm_convert_lock_handler()` handles incoming conversion messages on the master node.
- `dlm_revert_pending_convert()` moves a failed pending conversion back to granted state and clears LVB flags.

## Core Behavior
`__dlmconvert_master()` requires `res->spinlock` and performs the actual queue decision. It rejects already-converting locks and locks not on the granted queue. Downconverts are granted in place. Upconverts are granted only if compatible with all granted locks and both current/target modes of converting locks; otherwise they move to `res->converting` unless `LKM_NOQUEUE` is set.

The file also manages lock value block semantics:
- EX lock conversion with `LKM_VALBLK` sets `DLM_LKSB_PUT_LVB` and copies into `res->lvb` on grant.
- PR/NL conversion with a non-NL target sets `DLM_LKSB_GET_LVB`.
- NL target conversion suppresses LVB fetch.

## Remote Protocol
`dlm_send_remote_convert_request()` builds `struct dlm_convert_lock`, optionally sends the LVB as a second kvec segment for `LKM_PUT_LVB`, and maps transport errors to DLM statuses. Host-down errors wait briefly for heartbeat recognition and return `DLM_RECOVERING`.

`dlm_convert_lock_handler()` validates domain state, name length, LVB flag combinations, resource state, and the lock identity on the granted queue before invoking `__dlmconvert_master()`. It reserves AST capacity while the conversion is in progress and queues AST/kicks the DLM thread after releasing locks.

## Locking and State
The file is explicit that only `__dlmconvert_master()` enters and exits with `res->spinlock` held. Public paths reserve/release AST slots, mark `DLM_LOCK_RES_IN_PROGRESS`, wake `res->wq`, and avoid holding spinlocks during network sends.
