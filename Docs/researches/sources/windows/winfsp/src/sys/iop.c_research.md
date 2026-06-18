# File Research: sources/windows/winfsp/src/sys/iop.c

## Role

Central IRP/request plumbing for WinFsp. This file allocates and frees `FSP_FSCTL_TRANSACT_REQ` objects, attaches them to IRPs, posts kernel work requests back through the filesystem-control path, completes IRPs, supports cancellation, stores retry responses, and dispatches major-function prepare/complete callbacks.

## Request Allocation

`FspIopCreateRequestFunnel` allocates a request header plus aligned transaction request and optional extra filename buffer. Requests and headers must be 16-byte aligned because low pointer bits are used for flags elsewhere. If required alignment exceeds pool alignment, the original allocation pointer is saved immediately before the aligned header.

Flags control:

- Must-succeed vs normal allocation.
- Paged vs nonpaged pool.
- Optional nonpaged work-item allocation.

The function zeroes header/request memory, stores the request finalizer and work item, fills request size and hint with the originating IRP pointer, copies an optional file name into `Request->Buffer`, sets `Request->FileName.Size`, asserts alignment, and attaches the request to the IRP.

`FspIopCreateRequestWorkItem` lazily adds a nonpaged work-item structure to an existing request.

`FspIopDeleteRequest` invokes the request finalizer with its context, frees saved retry response, frees work item, restores the original allocation pointer if over-aligned, and frees the allocation.

`FspIopResetRequest` runs the old finalizer, clears request context, and installs a new finalizer while preserving the request object.

## Posting Work Requests

`FspIopPostWorkRequestFunnel` creates a kernel IRP targeting a device object and sends it as `IRP_MJ_FILE_SYSTEM_CONTROL` with `FSP_FSCTL_WORK` or `FSP_FSCTL_WORK_BEST_EFFORT`. It passes the request through method-neither input, installs a completion routine that frees the IRP, and deletes the request itself if `IoCallDriver` does not return pending.

This path is used for internal work requests not directly attached to an existing user IRP.

## Completion And Cancellation

`FspIopCompleteIrpEx` deletes any attached request, extracts the device object before completion, updates create statistics when appropriate, zeroes `IoStatus.Information` for most non-success statuses, sets final status, completes the IRP, and optionally dereferences the device object.

`FspIopCompleteCanceledIrp` logs cancellation, enters filesystem context, sets the top-level IRP to the canceled IRP, completes it with `STATUS_CANCELLED`, restores the old top-level IRP, and exits filesystem context. This protects request finalizers that release ERESOURCE locks.

## Retry Support

`FspIopRetryPrepareIrp` reposts an IRP to the IOQ best-effort path when preparation must be retried.

`FspIopRetryCompleteIrp` saves a copy of the user-mode response in the request header via `FspIopSetIrpResponse`, then asks the IOQ to retry completion later.

`FspIopIrpResponse` retrieves the saved copied response.

This is used by files such as `fileinfo.c`, `dirctl.c`, and `security.c` when they cannot reacquire locks during completion.

## Dispatch Tables

`FspIopDispatchPrepare` and `FspIopDispatchComplete` call major-function-specific function pointers from `FspIopPrepareFunction` and `FspIopCompleteFunction`. Completion rejects pending/private/ignore statuses in user responses by rewriting them to `STATUS_INTERNAL_ERROR` before dispatching.

The file defines the global prepare and complete function arrays sized to `IRP_MJ_MAXIMUM_FUNCTION + 1`.

## Integration Points

This module is the common substrate for all user-mode WinFsp transactions. Other dispatch files create requests with finalizers, store lock/resource/token state in the request context, post to IOQ, and rely on this file to clean up on success, failure, cancellation, or retry.

## Edge Cases And Risks

- Correctness depends on request finalizers being idempotent with context fields cleared by completion helpers before normal release.
- Over-alignment stores the original allocation pointer in the slot before the aligned header; any layout change must preserve this convention.
- `FspIopPostWorkRequestFunnel` deletes the request when the lower driver does not pend, because ownership only transfers on pending.
- Cancellation completion explicitly wraps filesystem enter/exit because cancels can arrive with APCs enabled.
