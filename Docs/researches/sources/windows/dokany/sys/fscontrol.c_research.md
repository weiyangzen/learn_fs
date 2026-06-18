# File Research: sources/windows/dokany/sys/fscontrol.c

Implements filesystem-control dispatch: oplock FSCTLs, Dokan global/volume/disk user FSCTL routing, event-pull batching, mount-volume creation, VPB initialization, and directory reparse-point FSCTL helpers.

Key entry points:
- `DokanDispatchFileSystemControl()` routes mount-volume and user filesystem requests.
- `DokanUserFsRequest()` chooses global, volume, or disk request handling based on the request context.
- `DokanGlobalUserFsRequest()` handles driver-wide controls such as event start/release, debug mode, version, mount list, and session cleanup.
- `DokanVolumeUserFsRequest()` handles keepalive activation, path notification, oplocks, simple volume controls, and selected network FSCTL forwarding.
- `DokanDiskUserFsRequest()` handles event process-and-pull, event release/write, volume metrics, timeout reset, and access token retrieval.
- `DokanProcessAndPullEvents()` completes an optional prior event reply, waits for queued work, and fills the current IOCTL buffer with queued `EVENT_CONTEXT` items.
- `PullEvents()` drains the notify queue into the user-mode output buffer, respecting IPC batching.
- `DokanOplockRequest()` validates and services oplock FSCTLs through `FsRtlOplockFsctrl()`.
- `DokanMountVolume()` creates the VCB volume device for a Dokan disk device and registers it with mount manager / UNC provider paths.
- `CreateSetReparsePointRequest()`, `CreateRemoveReparsePointRequest()`, and `SendDirectoryFsctl()` manage directory mount-point reparse data.
- `DokanInitVpb()` initializes VPB fields for a mounted volume.

Core mechanics:
- Oplock request handling validates CCB/FCB/VCB/DCB identity, rejects invalid directory oplocks, checks delete-pending state, and may include byte-range lock state in `oplockCount`.
- `FSCTL_REQUEST_OPLOCK` input/output sizes are explicitly validated for modern oplock requests.
- `FSCTL_ACTIVATE_KEEPALIVE` activates only the special keepalive FCB and prevents multiple active keepalive handles.
- `FSCTL_NOTIFY_PATH` lets user mode inject a path change notification and cleans all waiters on invalid object-name status.
- Event pulling uses `Dcb->NotifyIrpEventQueue` as the waitable signal and `Dcb->NotifyEvent.ListHead` as the actual work queue.
- Mount-volume walks lower device objects to find a DCB even if a filter wraps the Dokan disk device.
- Mounting creates the VCB, initializes FCB table, notify state, advanced FCB header, VPB, direct I/O, mount-entry volume pointer, timeout thread, mount-manager arrival, and network UNC provider registration.

Important invariants:
- After `FsRtlOplockFsctrl()`, Dokan no longer owns the IRP and sets `DoNotComplete`.
- Event-pull output must have room for at least `EVENT_CONTEXT`.
- The notify queue is reflagged when events remain after a partial pull.
- Mount entries must exist when `DokanMountVolume()` links a VCB to the DCB.
- Directory mount-point reparse operations temporarily clear top-level IRP state to avoid recursive filesystem issues.

Filesystem relevance:
- This file connects Dokan to Windows filesystem-control infrastructure, including mount recognition, oplocks, change notification injection, driver control IOCTLs, and the main event-pull loop used by user-mode filesystems.

Notable risks:
- Oplock and byte-range-lock interactions depend on exact lock ordering and FsRtl ownership semantics.
- Mount-volume lower-device probing intentionally reduces noise after a first successful mount but can obscure startup failures.
- Event-pull batching must preserve queued items when the current user buffer is too small.
