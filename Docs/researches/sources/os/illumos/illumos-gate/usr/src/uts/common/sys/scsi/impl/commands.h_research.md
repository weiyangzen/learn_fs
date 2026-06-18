# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/commands.h

This implementation-specific command header defines `union scsi_cdb`, CDB field aliases, big-endian unaligned read/write helpers, command-forming macros, direct-access defect/capacity structures, and kernel command setup functions.

Key definitions:
- Defines `SCSI_CDB_SIZE` as group 4 size and keeps deprecated `CDB_SIZE`.
- `union scsi_cdb` overlays CDBs as:
  - generic opaque byte array
  - word array
  - common command/lun/tag fields
  - group 0, group 1/2, group 4, and group 5 structured layouts
- Provides numerous field alias macros for legacy accessors.
- Provides `SCSI_READ16/24/32/40/48/64` and `SCSI_WRITE16/24/32/40/48/64` macros for unaligned big-endian protocol fields.
- Provides CDB field construction/extraction macros for group 0/1/4/5 addresses and counts.
- Provides legacy `MAKECOM_*` packet/CDB construction macros.
- Defines format/defect list structures and capacity structures including 16-byte read capacity response.
- Declares kernel helper functions `makecom_*` and `scsi_setup_cdb()`.

Dependencies:
- Included by `generic/commands.h`.
- Relies on command group constants from the generic command header include order.

Impact:
- This is a foundational SCSA command construction API.
- Its macros influence many target and HBA drivers that build CDBs directly.

Cautions:
- Many macros expand to comma expressions or multiple assignments and must be used carefully in statement contexts.
- Legacy `MAKECOM_*` macros are pre-SCSI-3 and comments recommend `scsi_setup_cdb()`.
- `SCSI_WRITE48` appears inconsistent: the macro parameter list names `Sr40_Val`, while the body references `Sr48_Val` in the high 32-bit expression and `Sr40_Val` in the low 16-bit expression. This should be treated cautiously by any consumer or refactor.
