# File Research: sources/windows/dokany/sys/notification.c

Implements event context allocation, notify queue insertion, pending IRP release/retry helpers, the retry notification thread, change-notification cleanup, FCB garbage collector stop, volume event release/unmount, and global mount-point release.

Key entry points:
- `AllocateEventContextRaw()` and `AllocateEventContext()` allocate driver-owned event records and initialize common event fields.
- `SetCommonEventContext()` fills mount id, major/minor IRP function, flags, file flags, and process id.
- `DokanEventNotification()` enqueues an event for user-mode pulling and signals `NotifyIrpEventQueue`.
- `MoveIrpList()` safely drains an `IRP_LIST`, filtering canceled IRPs and preserving forced-canceled create entries for later completion.
- `ReleasePendingIrp()`, `ReleaseNotifyEvent()`, and `RetryIrps()` cancel pending IRPs, free queued notification events, or redispatch retry IRPs.
- `NotificationThread()` waits for release or retry work and redispatches pending retry IRPs.
- `DokanStartEventNotificationThread()` and `DokanStopEventNotificationThread()` manage the retry notification thread.
- `DokanCleanupAllChangeNotificationWaiters()` wraps `FsRtlNotifyCleanupAll()`.
- `DokanEventRelease()` performs the core unmount/release sequence for a mounted volume.
- `DokanGlobalEventRelease()` resolves a mount point to a mounted volume and invokes `DokanEventRelease()`.
- `GetCurrentSessionId()` reads the requestor session id.

Core mechanics:
- `DRIVER_EVENT_CONTEXT` embeds `EVENT_CONTEXT`; allocation size accounts for variable-length operation payloads.
- Notification events are protected by spin locks, while user-mode waiters block on a kernel queue.
- Release cancels pending normal/retry IRPs, frees notification events, stops timeout and notification threads, rundowns the event queue, stops FCB garbage collection, clears mounted state, deletes lookaside lists, cleans directory notification waiters, drains the remove lock, and queues device deletion.
- Global release accepts a mount-point intermediate string, normalizes drive letters to `\DosDevices\X:`, session-scopes lookup, verifies mounted state, and rejects busy/not-mounted devices.

Important invariants:
- Event contexts are freed by converting back to containing `DRIVER_EVENT_CONTEXT`.
- Forced-canceled create IRPs must not be dropped when draining lists; they still require create-cancel completion.
- Unmount sets both `VCB_DISMOUNT_PENDING` and `DCB_DELETE_PENDING` before releasing queues and stopping threads.
- Remove lock is acquired before release work and released with wait before device deletion.

Filesystem relevance:
- This is the teardown and event-notification control plane for Dokan volumes. It ensures user-mode events, retries, directory notifications, and pending IRPs are drained when a filesystem exits or unmounts.

Notable risks:
- Unmount ordering is complex; mount-point deletion must happen before pending IRP release for mount-manager interactions.
- `DokanStopEventNotificationThread()` only waits when `KeSetEvent()` reports previous signal state greater than zero, which may deserve scrutiny.
- Global release depends on mount-entry volume pointers being populated after successful mount.
