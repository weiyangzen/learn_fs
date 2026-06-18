# File Research: sources/windows/winfsp/src/sys/volume.c

This file implements WinFsp kernel volume lifecycle and the kernel/user-mode transaction bridge for file-system requests.

Key responsibilities:
- Creates volume devices from encoded `FSP_FSCTL_VOLUME_PARAMS`, normalizing defaults for sector size, allocation unit size, component length, timeouts, IRP capacity, cache timeout fields, network prefixes, and release-build buffering policy.
- Creates the fsvol device and, for disk file systems, the paired fsvrt disk device with secure device naming and sector-size setup.
- Registers network file systems with the WinFsp MUP path and creates symbolic links for named volumes.
- Handles teardown: stops the IOQ, finalizes mountdev state, unregisters MUP/symbolic links, swaps or delays VPB destruction, forces active file sections closed, releases notify/rename ownership, and dereferences device objects.
- Mounts virtual disk volumes by matching the fsvrt device to a live fsvol device, patching the VPB, setting the serial number, and compensating for the extra reference passed in the mount IRP.
- Supports mountdev and mount-manager integration, including persistent mountdev setup, drive-letter/directory mount creation, registry-gated mount-manager use from the FSD, and cleanup of mount points.
- Returns single volume names and volume lists, appending network volume prefixes where applicable.
- Implements the main transact loop used by user-mode file systems: consumes responses, completes processing IRPs, handles retried/reposted IRPs, waits for pending IRPs, prepares requests, copies them to user buffers or internal buffers, and moves IRPs into the processing queue.
- Dispatches extension-provider control codes through `Provider->DeviceTransact`.
- Implements two-phase stopping via `FSP_FSCTL_STOP0` and `FSP_FSCTL_STOP`, avoiding premature cancellation of IRPs still visible to user-mode dispatcher threads.
- Handles asynchronous volume notifications by copying user buffers into nonpaged work items, taking rename/delete coordination locks, validating notify file names, invalidating file-node caches, and issuing change notifications.
- Posts kernel-owned work requests via `FspVolumeWork`.

Important dependencies:
- `FspDeviceCreate`, `FspDeviceInitialize`, `FspDeviceReference`, and global device-list helpers.
- `FspIoq*` queue primitives for pending, processing, retried, stopped, timeout, and cancellation state.
- `FspIopDispatchPrepare` / `FspIopDispatchComplete` for request/response handoff.
- Mount helpers such as `FspMountdevMake`, `FspMountdevFini`, `FspMountmgrCreateDrive`, and `FspMountmgrNotifyCreateDirectory`.
- Name/cache helpers such as `FspFileNameIsValid` and `FspFileNodeInvalidateCachesAndNotifyChangeByName`.
- Silo globals and MUP registration for network file systems.

Filesystem relevance:
- This is the control-plane core for a WinFsp file system instance.
- It defines how a user-mode file-system process creates a kernel volume, how Windows mounts it, how user-mode receives kernel IRP requests, and how user-mode responses complete those IRPs.
- The transaction path is especially central: most ordinary file operations prepared elsewhere eventually flow through this file to cross the kernel/user boundary.

Notable watchpoints:
- Volume creation decodes binary volume parameters through specially encoded `WCHAR` values in the create path; validation failures return `STATUS_INVALID_PARAMETER`.
- Release builds force `AlwaysUseDoubleBuffering` to avoid unsafe read behavior.
- `RejectIrpPriorToTransact0` is hardcoded on, so early IRP acceptance depends on transaction readiness.
- VPB lifetime is delicate: teardown may free immediately, release a mount reference, or schedule delayed cleanup depending on reference count.
- `FspVolumeFastTransact` must preserve forward progress while handling reposted/retried IRPs, bogus hints, stopped queues, internal transactions, and buffer-size limits.
- `FspVolumeNotify` intentionally defers work to avoid deadlocks with locks already held by file-system request handlers.
