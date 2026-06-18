# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_ctl.h

## Purpose
Declares SCSI control operations for capabilities, abort/reset, task management, ACA clearing, and unit-address reporting.

## Main Interfaces
- Reset levels: `RESET_ALL`, `RESET_TARGET`, `RESET_BUS`, `RESET_LUN`.
- Reset notification flags: `SCSI_RESET_NOTIFY`, `SCSI_RESET_CANCEL`.
- `SCSI_MAXNAMELEN`, `SCSI_NO_QUIESCE`.
- Kernel functions: `scsi_ifgetcap`, `scsi_ifsetcap`, `scsi_abort`, `scsi_reset`, `scsi_reset_notify`, `scsi_clear_task_set`, `scsi_terminate_task`, `scsi_clear_aca`, `scsi_ua_get_reportdev`, `scsi_ua_get`.

## Dependencies And Relationships
Includes `sys/scsi/scsi_types.h`. The declared functions route through HBA transport vectors in `scsi_hba_tran`.

## Research Notes
Separates bus reset from broader target/LUN reset levels and documents invocation paths.

## Notable Risks
- Reset and task-management calls can disrupt outstanding I/O and reservations.
- `SCSI_NO_QUIESCE` changes hotplug behavior and should be treated as a policy override.
