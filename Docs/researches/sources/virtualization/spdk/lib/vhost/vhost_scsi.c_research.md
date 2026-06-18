# File Research: sources/virtualization/spdk/lib/vhost/vhost_scsi.c

## Purpose
Implements SPDK's vhost-user SCSI backend. It creates vhost SCSI controllers, maps SCSI targets/LUNs to bdev-backed `spdk_scsi_dev` objects, processes virtio-scsi request/control/event queues, and coordinates target hotplug, resize, and hotremove across active sessions.

## Key Elements
Defines device-level `spdk_vhost_scsi_dev`, session-level `spdk_vhost_scsi_session`, target state structs, and per-request `spdk_vhost_scsi_task`. Target state uses `VHOST_SCSI_DEV_EMPTY`, `ADDING`, `PRESENT`, `REMOVING`, and `REMOVED` to distinguish global and per-session lifecycle.

Feature negotiation advertises base vhost features plus virtio-scsi INOUT, HOTPLUG, CHANGE, and T10 PI, while T10 PI is explicitly disabled. Protocol features include vhost-user inflight shared memory.

The request path is split queue based. `vdev_worker` scans request queues from `VIRTIO_SCSI_REQUESTQ` onward. `vdev_mgmt_worker` periodically processes removed devices, eventq signaling, and controlq requests. `process_vq` handles inflight resubmit descriptors, fetches available descriptors, marks split-ring inflight entries, and calls `process_scsi_task`.

`task_data_setup` parses virtio-scsi command descriptors into SPDK SCSI task fields. It supports FROM_DEV layout `[req][resp][write buffers...]`, TO_DEV layout `[req][read buffers...][resp]`, no-payload read commands, response buffer validation, iovec conversion, length/transfer accounting, and invalid descriptor rejection. Completions copy SCSI status/sense/residual data into the virtio response and enqueue the used descriptor.

Control queue handling supports TMF logical unit reset through SPDK SCSI management tasks. Unsupported TMF and async notification query/subscribe paths return aborted responses.

Target management APIs create controllers, optionally delay socket start, start delayed controllers, add targets by slot or first free slot, remove targets asynchronously, and query target pointers. Adding a target constructs a one-LUN `spdk_scsi_dev`, adds a vhost port, allocates I/O channels per active session, and sends hotplug events when negotiated. Removal marks targets as removing, sends hotremove events, waits for pending tasks to drain, frees per-session I/O channels, destructs the SCSI device, and completes optional callbacks.

## Dependencies
Depends on Linux `virtio_scsi.h`, SPDK env/thread/SCSI/SCSI spec/util/likely/vhost APIs, and shared vhost helpers from `vhost_internal.h`.

## Behavior/Risks
Only one LUN per target is constructed. Target numbers are bounded by `SPDK_VHOST_SCSI_CTRLR_MAX_DEVS` and negative add requests choose the first free slot.

Hotremove is intentionally asynchronous. A globally removing target remains until every active session drops its local device reference and pending SCSI tasks are gone. Session stop has to handle targets in `REMOVING` state and may trigger another foreach-session detach attempt.

The SCSI request path assumes split-ring descriptor helpers; this file does not implement packed-ring SCSI request parsing. Invalid descriptors, missing response buffers, bad LUN format, missing target, and invalid transfer direction produce bad-target, aborted, or used-ring zero-length completions depending on where validation fails.

Session shutdown waits for task count and the vhost-user device lock, with a timeout. If I/O channel allocation fails for a target in one session, that session silently treats the target as absent while other sessions may still use it.
