# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/vhost_scsi.c

Registers SPDK vhost SCSI as an event subsystem.

Key elements:
- Initializes through `spdk_vhost_scsi_init()`.
- Finishes through `spdk_vhost_scsi_fini()`.
- Writes config JSON through `spdk_vhost_scsi_config_json()`.
- Registers subsystem name `vhost_scsi`.

Dependencies:
- Declares dependency on `scsi`.

Research notes:
- Relies on the SCSI subsystem rather than directly on bdev.
