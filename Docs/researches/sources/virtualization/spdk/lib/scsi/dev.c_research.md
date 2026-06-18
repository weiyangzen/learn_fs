# File Research: sources/virtualization/spdk/lib/scsi/dev.c

This file manages SPDK SCSI device objects, their LUN lists, ports, I/O channel allocation, task forwarding, and destruction.

Devices come from a static `g_devs[SPDK_SCSI_MAX_DEVS]` array. `allocate_dev()` finds the first unallocated slot, clears it, assigns the array index as device ID, marks it allocated, and initializes the LUN tailq. `free_dev()` requires the device to be allocated and marked removed, clears allocation state, and runs an optional remove callback.

Device destruction is asynchronous with respect to LUN lifetime. `spdk_scsi_dev_destruct()` marks the device removed, stores the completion callback/context, and either frees immediately if no LUNs exist or asks each LUN to destruct. LUNs remove themselves from the device when their outstanding work is drained; the device is freed when the last LUN is deleted.

LUN allocation preserves sorted LUN order. `scsi_dev_find_free_lun()` either finds the lowest free LUN ID for `-1` or validates a requested ID is unused, returning the preceding LUN for insertion. `spdk_scsi_dev_add_lun_ext()` validates ID range, constructs a LUN from a bdev name, assigns explicit or derived ID, links it to the device, and inserts it in sorted order. Construction of a full device validates name length, nonzero LUN count, mandatory LUN 0, and non-null bdev names before adding each LUN; failure destructs the partially built device.

Task entry points are simple routing functions: management tasks go to `scsi_lun_execute_mgmt_task()`, normal tasks go to `scsi_lun_execute_task()`.

Port management uses fixed slots inside the device. Adding a port checks max count, duplicate ID, finds a free slot, calls `scsi_port_construct()`, and increments `num_ports`. Deleting finds by ID, destructs the port slot, and decrements `num_ports`. Lookup iterates used slots by port ID.

I/O channel allocation and free iterate all LUNs. If any LUN channel allocation fails, previously allocated LUN channels are freed. Device accessors expose name, ID, specific LUN, first active LUN, next active LUN, and whether any LUN has pending normal or management tasks for an optional initiator port.

The key invariants are requiring LUN 0 for a SCSI device, preserving sorted LUN IDs, not returning LUNs that are removing, waiting for LUN teardown before freeing a removed device, and rolling back all LUN channels if device-wide channel allocation fails.
