# File Research: sources/windows/dokany/dokan/close.c

Dispatcher for `IRP_MJ_CLOSE`, handling final open-context release without sending a reply to the driver.

Key responsibilities:
- Normalizes the close file name with `CheckFileName()`.
- Emits debug information about the close and associated open event.
- Calls `ReleaseDokanOpenInfo()` to decrement open tracking and run delayed `CloseFile` callback when safe.

Important behavior:
- Does not allocate or send `EVENT_INFORMATION`; the driver has already completed close and expects no reply.
- Actual user `CloseFile` invocation may be delayed until all in-flight operations on the same `DOKAN_OPEN_INFO` have released their references.

Dependencies:
- Uses `DOKAN_OPEN_INFO` lifetime logic from `dokan.c`.
- Includes `dokan_pool.h` for pooled open-info cleanup functions used indirectly.

Notable risks:
- Correctness relies on `ReleaseDokanOpenInfo()` balancing the extra close decrement against prior per-event increments.
- Because no result is returned to the driver, failures inside user `CloseFile` cannot be reported.
