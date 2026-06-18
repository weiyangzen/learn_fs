# File Research: sources/virtualization/spdk/lib/scsi/scsi_internal.h

This private SCSI header defines the internal data model shared by the SPDK SCSI library: ports, devices, LUN descriptors, LUN state, persistent reservation registrants/reservation state, and internal function prototypes.

`struct spdk_scsi_port` stores use state, numeric ID, relative target port index, transport ID bytes, and port name. `struct spdk_scsi_dev` owns allocation/removal state, device name, the LUN list, up to `SPDK_SCSI_DEV_MAX_PORTS` port entries, and protocol ID. `struct spdk_scsi_lun_desc` tracks open LUN descriptors and hot-remove callbacks.

`struct spdk_scsi_lun` is the central runtime object. It contains LUN identity and removal/resizing flags, owning device, associated bdev/descriptor/thread/channel, hot-remove and resize callbacks, open descriptors, submitted and pending task queues, submitted and pending management task queues, reset poller, refcount, persistent reservation generation, registrant list, current reservation, and an embedded SPC-2 reservation holder.

Persistent reservation structures distinguish registrants by I_T nexus using initiator and target ports plus copied names/transport IDs. `struct spdk_scsi_pr_reservation` stores flags, holder, reservation type, and current reservation key. `SCSI_SPC2_RESERVE` marks legacy SPC-2 reservations.

The declaration surface ties the library together: LUN construct/destruct, task and management task execution/completion, pending-task queries, I/O channel allocation/free, device list access, port construct/destruct, bdev-backed SCSI execution/reset/DIF context helpers, persistent reservation IN/OUT/check functions, and SPC-2 reserve/release/check functions.

The key invariant is that most SCSI internals operate on thread-affine LUN state and queue membership. Reservation code relies on stable `spdk_scsi_port` pointers for live nexus matching while also storing copied names/transport IDs for reporting.
