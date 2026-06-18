# File Research: sources/windows/dokany/dokan/cleanup.c

Dispatcher for `IRP_MJ_CLEANUP`, bridging kernel cleanup notifications to the user filesystem callback.

Key responsibilities:
- Normalizes the cleanup file name with `CheckFileName()`.
- Allocates a default `EVENT_INFORMATION` reply through `CreateDispatchCommon()`.
- Forces the reply status to `STATUS_SUCCESS`, regardless of user callback behavior.
- Transfers `DOKAN_DELETE_ON_CLOSE` into `DOKAN_FILE_INFO.DeletePending`.
- Invokes `DOKAN_OPERATIONS.Cleanup` when implemented.
- Completes the event through `EventCompletion()`.

Important behavior:
- Cleanup is treated as non-failing: user callback return value is ignored because the callback returns `void`.
- Delete-on-close is exposed to user mode before the cleanup callback so the filesystem can delete the object at cleanup time.
- Open-info lifetime is released through the common completion path.

Dependencies:
- Uses `DOKAN_IO_EVENT`, `EVENT_CONTEXT.Operation.Cleanup`, and `DOKAN_FILE_INFO`.
- Depends on core helpers declared in `dokani.h`: `CheckFileName`, `CreateDispatchCommon`, and `EventCompletion`.

Notable risks:
- Cleanup correctness depends on the user filesystem honoring `DeletePending`; the library cannot recover from a failed delete in this callback.
- The event result allocation is assumed to succeed; this function does not explicitly handle `CreateDispatchCommon()` allocation failure.
