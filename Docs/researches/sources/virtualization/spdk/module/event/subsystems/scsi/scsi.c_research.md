# File Research: sources/virtualization/spdk/module/event/subsystems/scsi/scsi.c

Registers the SPDK SCSI layer as an event subsystem.

Key elements:
- Initializes through `spdk_scsi_init()`.
- Finishes through `spdk_scsi_fini()`.
- Registers subsystem name `scsi`.

Dependencies:
- Declares dependency on `bdev`.

Research notes:
- This subsystem underpins iSCSI and vhost SCSI integration.
