# File Research: sources/windows/dokany/dokan/dokani.h

Main internal Dokan runtime header defining mount instances, open contexts, batched IO buffers, per-event state, and dispatcher/helper prototypes.

Key responsibilities:
- Includes Windows, standard IO, public Dokan API, debug/control header, list helpers, and vector API.
- Defines `DOKAN_INSTANCE_THREADINFO` for per-instance threadpool association.
- Defines `DOKAN_INSTANCE`, the mount-level runtime object holding device names, mount point, UNC name, IDs, options, callbacks, device handles, threadpool cleanup state, notify/keepalive handles, stop flag, and unmount callback guard.
- Defines `DOKAN_OPEN_INFO`, the per-open object carrying directory cache, search pattern, user context, event ID, directory flag, open count, delayed close data, and original event context.
- Defines `DOKAN_IO_BATCH`, the shared buffer returned from driver event pulls, including batch byte count, main-pull flag, pool ownership, event-context refcount, and flexible event context storage.
- Defines `DOKAN_IO_EVENT`, the per-dispatched operation state linking mount instance, optional open info, event result buffer, pool ownership, file info, event context, and owning batch.
- Defines `IOEVENT_RESULT_BUFFER_SIZE()`.
- Declares internal lifecycle, mount, device, dispatch, completion, name normalization, open-info release, and unmounted notification helpers.

Important behavior:
- `DOKAN_IO_EVENT.EventContext` is owned by its `DOKAN_IO_BATCH`, not by the event itself.
- `DOKAN_OPEN_INFO` owns cached directory enumeration state and must survive across related operations until close.
- Some events, notably close, intentionally have no `EventResult`.
- Batch lifetime is tied to `EventContextBatchCount`.

Dependencies:
- Internal structs depend directly on driver protocol structs such as `EVENT_CONTEXT` and `EVENT_INFORMATION`.
- Exposes dispatcher prototypes implemented in multiple C files in this group and adjacent Dokan files.

Notable risks:
- Raw pointer contexts are exchanged with the kernel via `EVENT_INFORMATION.Context`; this is inherently process-local and requires matching driver/user assumptions.
- Lifetime coupling between `DOKAN_IO_EVENT`, `DOKAN_IO_BATCH`, and `DOKAN_OPEN_INFO` is subtle and must be maintained by every dispatcher.
- The header centralizes many internal APIs, so unrelated modules can easily depend on implementation details.
