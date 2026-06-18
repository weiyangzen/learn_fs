# File Research: sources/virtualization/spdk/lib/scsi/task.c

This file implements common SCSI task lifetime, task data movement, sense/status construction, and fallback handling for null LUN or aborted tasks.

Task construction installs completion and free callbacks, increments the task reference count, and initializes the scatter-gather view to point at the embedded single iovec. `spdk_scsi_task_put()` decrements the refcount, frees any attached bdev I/O, releases DMA-allocated task data, and calls the task-specific free callback when the count reaches zero.

Data helpers support both internal allocation and caller-provided iovecs. `spdk_scsi_task_scatter_data()` allocates a DMA buffer for simple one-iovec tasks with no buffer, verifies total iovec capacity, copies source bytes across iovecs, and sets illegal-request sense on short capacity. `spdk_scsi_task_gather_data()` copies all iovec data into a newly allocated contiguous buffer for command parsers such as MODE SELECT or PR OUT. `spdk_scsi_task_set_data()` attaches an external single buffer when no task allocation exists.

Sense data is fixed-format current sense. `spdk_scsi_task_build_sense_data()` fills response code, sense key, ASC, ASCQ, and an 18-byte sense length. `spdk_scsi_task_set_status()` builds sense data automatically for CHECK CONDITION, and `spdk_scsi_task_copy_status()` copies sense/status from one task to another.

`spdk_scsi_task_process_null_lun()` handles commands addressed to unsupported LUNs. INQUIRY returns a peripheral qualifier of unsupported/logical unit not connected with device type unknown, bounded by allocation length; other commands return CHECK CONDITION with logical unit not supported. `spdk_scsi_task_process_abort()` sets aborted-command sense.

The main invariants are task refcount ownership, avoiding double-free of `bdev_io` and DMA task buffers, and ensuring generated sense data matches the status returned to upper-layer protocols.
