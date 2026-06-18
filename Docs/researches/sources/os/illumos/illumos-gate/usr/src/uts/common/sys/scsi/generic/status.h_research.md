# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/status.h

This header defines SCSI status byte layout, auto-request-sense status layout, and status code masks/constants.

Key definitions:
- `struct scsi_status` maps the one-byte SCSI status block into endian-dependent bitfields for check condition, condition met, busy, intermediate status, SCSI-2 modifier, and vendor/reserved bits.
- `struct scsi_arq_status` combines original command status, request-sense packet status/reason/residue/state/statistics, and embedded extended sense data.
- Defines `SECMDS_STATUS_SIZE`.
- Defines byte-level status constants such as good, check, met, busy, intermediate, reservation conflict, terminated, queue full, ACA active, and task abort.
- Includes implementation-specific status deviations.

Dependencies:
- Uses `struct scsi_extended_sense` from generic sense definitions.
- Includes `sys/scsi/impl/status.h`.

Impact:
- Used by SCSA packet completion and error handling, especially when auto-request-sense is enabled.

Cautions:
- Status bitfields are compiler/bit-order dependent; byte masks are safer for raw status values.
