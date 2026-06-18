# File Research: sources/virtualization/spdk/lib/scsi/lun.c

This file implements SPDK SCSI LUN lifecycle, task ordering, management-task handling, hot-remove behavior, bdev event handling, LUN descriptors, and I/O channel ownership.

Normal task completion removes the task from the LUN outstanding task queue, records a trace event, and calls the task completion function. Management task completion removes the task from the outstanding management queue, calls its completion function, and then attempts to run the next pending management task.

The LUN maintains separate queues for pending normal tasks, outstanding normal tasks, pending management tasks, and outstanding management tasks. Only one management task is executed at a time. If no pending management task exists after one completes, pending normal tasks are flushed. Reset management tasks call `bdev_scsi_reset()` and, if successful, may wait on a poller until all prior outstanding normal tasks complete before completing the management task. Unsupported management functions are rejected as not supported.

Normal command execution sets initial GOOD status, traces start, links the task into outstanding tasks, and then checks removal, resize unit attention, and reservation rules before forwarding to `bdev_scsi_execute()`. Removed LUNs abort tasks. Resize events cause the next eligible command other than Inquiry, Report LUNs, or Request Sense to complete with UNIT ATTENTION / capacity data changed and then clear the resizing flag. SPC-2 reservations or persistent reservations are checked before bdev execution.

Task submission preserves ordering around management tasks. If management work is pending, normal tasks are appended and wait. If normal tasks are already pending, a new task is appended and the queue is flushed in order. Otherwise the task executes immediately.

Hot-remove is carefully staged. A bdev remove event marks the LUN removed, sends execution to the LUN’s I/O-channel thread if needed, flushes previously queued tasks as aborts, waits for outstanding normal and management work through a poller, notifies the top-level hotremove callback and all open descriptors, waits for any I/O channel to be released, then closes the bdev descriptor, removes the LUN from its device, and frees the LUN. Persistent reservation registrants are freed during final removal.

Resize bdev events set `lun->resizing = true` and call an optional resize callback. Unsupported bdev events are logged.

`scsi_lun_construct()` validates bdev name, allocates a LUN, opens the bdev write-enabled with `spdk_bdev_open_ext()` and `bdev_event_cb`, stores the constructing thread, initializes all queues and descriptor/registrant lists, stores bdev and callback state, and starts with no I/O channel. `scsi_lun_destruct()` enters the same hot-remove path.

LUN descriptors are lightweight open handles with optional hotremove callbacks. Open allocates and inserts a descriptor; close removes and frees it, asserting that if no descriptors remain then no I/O channel is still held.

I/O channels are single-thread owned. Allocation reuses an existing channel only on the same SPDK thread and increments a refcount; allocation from another thread fails. Free requires the same thread, decrements the refcount, and releases the bdev channel at zero. Descriptor-level public wrappers delegate to the underlying LUN.

Accessors return LUN ID, bdev name, parent device, removing state, and DIF context via bdev SCSI helpers. Pending-task queries can include both pending and outstanding queues and can filter by initiator port.

Important invariants are management-task serialization, reset waiting for prior outstanding I/O, no new useful I/O after `removed` is set, descriptor/channel lifetime during hot-remove, same-thread I/O channel free, and delivering resize unit attention exactly once for eligible commands.
