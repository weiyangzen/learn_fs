# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmconvert.c

## Purpose

`dlmconvert.c` implements OCFS2 DLM lock conversion: changing an already granted lock from one mode to another, either on the local lock-resource master or by sending a remote convert request to the master node.

It is responsible for moving locks between the granted and converting queues, preserving lock value block behavior, reserving/releasing AST capacity, and coordinating retry semantics when recovery or migration interrupts conversion.

## Main Entry Points

- `dlmconvert_master()` handles conversion when the local node owns the lock resource.
- `dlmconvert_remote()` handles conversion when another node owns the lock resource.
- `dlm_convert_lock_handler()` handles `DLM_CONVERT_LOCK_MSG` on the master node.
- `dlm_revert_pending_convert()` restores a failed pending conversion to the granted queue.

The central implementation is `__dlmconvert_master()`, which requires `res->spinlock` held on entry and keeps it held on exit.

## Conversion Logic

`__dlmconvert_master()` enforces two key preconditions before conversion:

- The lock must not already have `ml.convert_type` set.
- The lock must be present on the lock resource granted queue.

Downconverts are granted immediately because the requested mode is less restrictive than or equal to the current mode. Upconverts are granted only if compatible with all other granted locks and all converting locks, including their requested conversion modes. Existing conversion requests take precedence.

If the upconvert cannot be granted immediately:

- `LKM_NOQUEUE` returns `DLM_NOTQUEUED`.
- Otherwise, the lock is moved from `res->granted` to `res->converting`, and `lock->ml.convert_type` records the requested mode.

Immediate grants update `lock->ml.type`, set `lksb->status = DLM_NORMAL`, move the lock to the tail of the granted list, and request AST delivery.

## LVB Handling

The file handles lock value block flags during conversion:

- Converting from `LKM_EXMODE` with `LKM_VALBLK` sets `DLM_LKSB_PUT_LVB` and copies the caller LVB into `res->lvb` on grant.
- Converting from `LKM_PRMODE` or `LKM_NLMODE` to a mode above `LKM_NLMODE` sets `DLM_LKSB_GET_LVB`.
- Converting to `LKM_NLMODE` clears `LKM_VALBLK` because there is no LVB fetch.

Remote conversion translates local LVB intent into wire flags `LKM_PUT_LVB` or `LKM_GET_LVB`.

## Remote Path

`dlmconvert_remote()` waits for the lock resource to be idle, rejects conversion during recovery, moves the local lock to the converting queue, marks `convert_pending`, and sends `DLM_CONVERT_LOCK_MSG`.

After the remote response:

- Non-normal status reverts the local queue move.
- `DLM_NOTQUEUED` is treated as a legitimate non-grant result.
- If the master returned success but recovery already moved the lock back, the function returns `DLM_RECOVERING` to retry.
- `convert_pending` is cleared before exit.

`dlm_send_remote_convert_request()` sends either a single convert message or a two-element vector when an LVB is being pushed.

## Network Handler

`dlm_convert_lock_handler()` runs on the lock-resource master. It validates the domain, name length, LVB flags, and resource state. It looks up the target lock on the granted queue by cookie and node, applies LVB get/put flags to the lock status block, reserves an AST, marks the lock resource in progress, and calls `__dlmconvert_master()`.

On failure it clears transient LVB flags. On success it either queues the AST or releases the reserved AST.

## Concurrency And Invariants

The file’s locking contract is explicit:

- Only `__dlmconvert_master()` requires `res->spinlock` held across entry and exit.
- Other entry points acquire and release locks internally.
- `DLM_LOCK_RES_IN_PROGRESS` serializes conversion with other resource operations.
- AST reservation via `__dlm_lockres_reserve_ast()` must be balanced by either `dlm_queue_ast()` or `dlm_lockres_release_ast()`.

Important invariants:

- A converting lock has `ml.convert_type != LKM_IVMODE`.
- A non-converting lock has `ml.convert_type == LKM_IVMODE`.
- Failed pending conversions must be restored to `res->granted`.
- Conversion is only legal for locks already granted.

## Dependencies

This file depends on:

- Lock resource and lock structures from `dlmcommon.h`.
- AST queuing and migration barriers from the wider DLM implementation.
- Network messaging through `o2net_send_message_vec()`.
- Master/resource behavior implemented in `dlmmaster.c`.
- Lock creation and public locking API behavior in `dlmlock.c`.
