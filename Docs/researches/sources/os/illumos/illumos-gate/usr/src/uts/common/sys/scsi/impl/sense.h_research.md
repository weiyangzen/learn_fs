# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/sense.h

This implementation-specific sense header defines illumos pseudo sense keys, sense buffer sizing constants, legacy Emulex aliases, descriptor templates, and format-neutral sense parsing prototypes.

Key definitions:
- Defines Sun pseudo sense keys for driver-detected fatal errors, timeouts, EOF/EOT/BOT, length errors, and wrong media.
- Defines `NUM_IMPL_SENSE_KEYS`, `SENSE_LENGTH`, `MAX_SENSE_LENGTH`, and `SUN_MIN_SENSE_LENGTH`.
- Provides legacy aliases for Emulex controller-specific extended sense fields.
- Defines `struct scsi_descr_template`.
- Declares descriptor-format helper `scsi_find_sense_descr()`.
- Declares format-neutral helpers for sense key, ASC, ASCQ, information, command-specific information, extended sense field access, and validation.
- Defines validation return codes and flags for unusable/fixed/descriptor sense, buffer overflow, and deferred sense.

Dependencies:
- Included by `generic/sense.h` after standard sense structures are defined.

Impact:
- Provides the implementation helper layer used by code that wants to parse fixed and descriptor sense without duplicating format checks.

Cautions:
- Pseudo sense keys exceed legal standard SCSI sense key values by design.
- Callers should validate buffer length/format before interpreting optional fields.
