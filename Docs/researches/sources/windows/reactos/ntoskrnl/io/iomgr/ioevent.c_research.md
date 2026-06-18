# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/ioevent.c

This file provides I/O manager wrappers for creating named executive event objects.

Internal helper:
- `IopCreateEvent` builds kernel object attributes with `OBJ_OPENIF | OBJ_KERNEL_HANDLE`, calls `ZwCreateEvent` with `EVENT_ALL_ACCESS`, references the resulting event object with `ObReferenceObjectByHandle`, then immediately drops the extra object reference while returning both the object pointer and the kernel handle.
- If event creation or object referencing fails, it returns `NULL`; on reference failure it also closes the handle.

Public APIs:
- `IoCreateNotificationEvent` calls `IopCreateEvent` with `NotificationEvent`.
- `IoCreateSynchronizationEvent` calls `IopCreateEvent` with `SynchronizationEvent`.

Research notes:
- Events are created initially signaled (`TRUE` in `ZwCreateEvent`).
- Returned handles are kernel handles because the helper always sets `OBJ_KERNEL_HANDLE`.
- The object pointer remains valid by virtue of the returned handle holding the object alive, despite the helper dereferencing the temporary object reference before returning.
