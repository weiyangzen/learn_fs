# File Research: sources/virtualization/spdk/module/event/subsystems/vhost_scsi/Makefile

Builds the vhost SCSI event subsystem library.

Key elements:
- Compiles `vhost_scsi.c`.
- Produces `event_vhost_scsi`.
- Uses shared object version `5.0`.
- Uses blank SPDK map file.

Dependencies:
- Included conditionally by parent Makefile when vhost is enabled.

Research notes:
- Runtime dependency on SCSI is declared in the C source.
