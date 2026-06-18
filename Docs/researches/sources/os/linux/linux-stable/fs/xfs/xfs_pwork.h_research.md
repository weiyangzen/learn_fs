# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_pwork.h

## Purpose
Declares the XFS parallel work abstraction.

## Main Types
`struct xfs_pwork_ctl` stores the workqueue, mount pointer, callback, waitqueue, outstanding work count, and first error. `struct xfs_pwork` embeds a `work_struct` plus a backpointer to the control object. `xfs_pwork_work_fn` is the caller-provided worker callback type.

## Public API
Declares initialization, queueing, polling, and destruction functions. Provides `XFS_PWORK_SINGLE_THREADED` and inline abort checks `xfs_pwork_ctl_want_abort` and `xfs_pwork_want_abort`.

## Usage Contract
Callers embed `struct xfs_pwork` in their own work records, queue each item through the control object, and can poll for completion before destroying the workqueue and checking the stored error.
