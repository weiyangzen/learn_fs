# File Research: sources/windows/dokany/dokan/lock.c

Implements `DispatchLock`, mapping lock-control requests to filesystem callbacks.

Key behavior:
- Initializes dispatch result and defaults status to `STATUS_NOT_IMPLEMENTED`.
- Handles:
  - `IRP_MN_LOCK`: calls `DokanOperations->LockFile`; non-success maps to `STATUS_LOCK_NOT_GRANTED`.
  - `IRP_MN_UNLOCK_SINGLE`: calls `DokanOperations->UnlockFile`; any implemented result is reported as success.
  - `IRP_MN_UNLOCK_ALL` and `IRP_MN_UNLOCK_ALL_BY_KEY`: no implementation in this layer.
- Logs unknown minor functions.
- Completes through `EventCompletion`.

Role in architecture:
- Provides byte-range lock/unlock plumbing between the driver and user callbacks.
- Ignores lock keys; code comments show key fields are intentionally not passed through.
