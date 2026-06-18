# File Research: sources/virtualization/spdk/module/bdev/virtio/bdev_virtio_scsi.c

## Purpose
Implements virtio-scsi bdevs for PCI, vhost-user, and vfio-user transports. One virtio-scsi controller can expose multiple SPDK bdevs, one per discovered target LUN0.

## State
- `struct virtio_scsi_dev`: virtio device, detected disk list, scan context, management poller, control queue ring, event queue buffers, removal state, callbacks.
- `struct virtio_scsi_disk`: SPDK bdev for one target, scan geometry, notification descriptor, removal state.
- `struct virtio_scsi_scan_base`: active target scan state, scan queue, retry state, command context, payload buffer, and callback.
- `struct bdev_virtio_io_channel`: one acquired request virtqueue and response poller.
- `struct virtio_scsi_io_ctx`: per-I/O command/TMF request and response wrappers.

## Device Initialization
`virtio_scsi_dev_init()` negotiates features, starts the virtio device with fixed control/event queues plus request queues, allocates the control ring, acquires control/event queues, posts event buffers, registers a management poller, registers the SPDK I/O device, and links the device globally.

## I/O Path
Reads/writes build SCSI READ/WRITE 10 or 16 depending on capacity. Reset uses a control-queue TMF logical unit reset. UNMAP builds an SCSI UNMAP parameter list in a bdev buffer and submits it if target scan found thin-provisioning support. Flush is advertised as supported in `io_type_supported()` but `_bdev_virtio_submit_request()` does not implement it and fails default submission.

Request queue completions call `spdk_bdev_io_complete_scsi_status()` with SCSI status and parsed sense key/ASC/ASCQ.

## Scan Flow
Target scan sends:
1. standard INQUIRY
2. TEST UNIT READY, or START STOP UNIT if not ready
3. VPD supported pages
4. block thin provisioning VPD for UNMAP support when available
5. READ CAPACITY 10, falling back to READ CAPACITY 16 for large devices

Full scans walk targets `0..63`. Hotplug/rescan events can enqueue specific target scans. Existing targets are not reconfigured if geometry changes.

## Event And Management Queues
The management poller sends TMF I/O from `ctrlq_ring`, receives TMF completions, and receives eventq messages. Events trigger full rescan on missed events, target rescan on transport reset/rescan, or bdev unregister on removed target.

## Removal And Fini
Device removal marks the controller removed, interrupts pending scans after the next completion, unregisters all child bdevs, and unregisters the I/O device once all LUNs are gone. Module fini is asynchronous and waits for all controllers to remove before `spdk_bdev_module_fini_done()`.

## Invariants And Risks
- Only LUN0 per target is scanned.
- Scan requests have five retries.
- `virtio_scsi_dev_scan_tgt()` sets `full_scan = true` even for a single-target scan path, causing scan-next logic to continue scanning subsequent targets.
- `bdev_virtio_io_type_supported()` advertises FLUSH, but submit does not implement FLUSH.
- Global device list is protected by `g_virtio_scsi_mutex`.
