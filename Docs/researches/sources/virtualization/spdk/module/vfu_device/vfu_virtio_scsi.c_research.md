# File Research: sources/virtualization/spdk/module/vfu_device/vfu_virtio_scsi.c

Implements the virtio-scsi device model over the common vfio-user virtio transport.

Key responsibilities:
- Registers the `virtio_scsi` SPDK vfio-user endpoint model.
- Exposes a virtio-scsi controller with task-management queue, event queue, and I/O queues.
- Maps SCSI targets to SPDK SCSI devices backed by bdevs.
- Polls virtqueues and dispatches SCSI commands/task management to SPDK SCSI.
- Supports hotplug, hotremove, and resize/change notifications through the virtio-scsi event queue.
- Provides device-specific config get/set and queue option setup.

Important structures:
- `struct virtio_scsi_endpoint`: embeds common `vfu_virtio_endpoint`, holds virtio-scsi config, up to 8 target slots, and ring poller.
- `struct virtio_scsi_target`: stores an SPDK SCSI device pointer.
- `struct virtio_scsi_req`: wraps `vfu_virtio_req`, embeds an `spdk_scsi_task`, and stores virtio-scsi command/TMF request and response pointers.

Queue model:
- Queue 0 is used for task management.
- Queue 1 is the event queue.
- Other queues are I/O queues.
- The polling path skips queue 1 because events are enqueued by explicit event helpers.

Request handling:
- `virtio_scsi_process_req()` routes queue 0 requests to `virtio_scsi_tmf_cmd_req()` and all other processed queues to `virtio_scsi_cmd_req()`.
- `virtio_scsi_cmd_data_setup()` validates command request/response descriptors, determines data direction from descriptor writeability, sets SPDK SCSI task IOVs, CDB pointer, transfer length, and response default.
- `virtio_scsi_cmd_lun_setup()` validates virtio LUN format, finds the target, locates port 0 and LUN, and attaches them to the SCSI task.
- `virtio_scsi_cmd_req()` queues regular SCSI tasks with `spdk_scsi_dev_queue_task()`.
- `virtio_scsi_tmf_cmd_req()` supports logical unit reset via `spdk_scsi_dev_queue_mgmt_task()` and rejects unsupported task-management subtypes.
- Completion callbacks populate virtio-scsi response status, sense data, residual length, then finish the virtio request and release the SCSI task.

Target and event handling:
- `vfu_virtio_scsi_add_target()` constructs an SPDK SCSI device with one LUN backed by a bdev, adds port 0, updates config, and sends a hotplug event if the virtio device is already attached.
- `vfu_virtio_scsi_remove_target()` either schedules hotremove on the virtio thread or destructs the SCSI device immediately when unattached.
- Resize and hotremove callbacks find the target number by LUN and send messages to the virtio thread.
- `vfu_virtio_scsi_eventq_enqueue()` consumes one descriptor from the event queue, writes a `virtio_scsi_event`, completes it, and flushes the event queue IRQ.

Lifecycle:
- `virtio_scsi_start()` allocates I/O channels for present SCSI devices and registers the ring poller.
- `virtio_scsi_stop()` unregisters the poller and frees SCSI I/O channels.
- Endpoint destruct destructs all remaining SCSI devices, destructs common endpoint state, and frees the endpoint.
- Endpoint init sets up common virtio endpoint state and initializes virtio-scsi config.

Integration:
- Uses common virtio vfio-user helpers for PCI/device/queue handling.
- Uses SPDK SCSI APIs for command execution and bdev-backed SCSI device construction.
- Registers endpoint ops in a constructor via `spdk_vfu_register_endpoint_ops(&vfu_virtio_scsi_ops)`.
- Fills PCI device ID with `PCI_DEVICE_ID_VIRTIO_SCSI_MODERN`.

Notes:
- Maximum target count is fixed at 8.
- Unsupported changes to `sense_size` or `cdb_size` are rejected.
- Event queue notification depends on negotiated `VIRTIO_SCSI_F_HOTPLUG` and `VIRTIO_SCSI_F_CHANGE`.
