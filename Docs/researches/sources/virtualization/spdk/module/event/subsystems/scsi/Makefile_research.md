# File Research: sources/virtualization/spdk/module/event/subsystems/scsi/Makefile

Builds the event SCSI subsystem library.

Key elements:
- Compiles `scsi.c`.
- Produces `event_scsi`.
- Uses shared object version `8.0`.
- Uses the blank SPDK map file.

Dependencies:
- Built via SPDK library make fragment.

Research notes:
- Runtime dependency on bdev is declared in the C source.
