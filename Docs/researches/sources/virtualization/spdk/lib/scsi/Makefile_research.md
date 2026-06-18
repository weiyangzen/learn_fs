# File Research: sources/virtualization/spdk/lib/scsi/Makefile

This Makefile builds the SPDK `scsi` library with shared object version `11.0` and map file `spdk_scsi.map`.

It compiles `dev.c`, `lun.c`, `port.c`, `scsi.c`, `scsi_bdev.c`, `scsi_pr.c`, `scsi_rpc.c`, and `task.c`. The files in this work item cover the device, LUN, port, and common SCSI utility portions; bdev command translation, persistent reservations, RPC, and task helpers are built as part of the same library but are outside this group.
