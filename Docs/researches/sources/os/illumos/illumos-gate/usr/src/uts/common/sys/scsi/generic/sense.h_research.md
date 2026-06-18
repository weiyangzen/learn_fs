# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/generic/sense.h

This header defines standard SCSI sense data structures, sense key constants, descriptor-format sense headers/descriptors, descriptor type constants, and includes implementation-specific sense helpers.

Key definitions:
- Defines legacy non-extended `struct scsi_sense`.
- Defines fixed-format `struct scsi_extended_sense` and constants for fixed/deferred/descriptor/vendor-specific sense formats.
- Provides `SCSI_IS_DESCR_SENSE()` helper.
- Defines standard sense key constants from no sense through reserved.
- Defines descriptor-format sense header and descriptor structures for:
  - information
  - command-specific information
  - sense-key-specific data
  - FRU
  - stream commands
  - block commands
  - ATA status return
  - vendor-specific data
- Defines descriptor type constants.
- Includes implementation-specific sense definitions.

Dependencies:
- Includes `impl/sense.h` at the end.
- Uses endian-dependent bitfield branches.

Impact:
- Central to SCSI error interpretation and auto-request-sense handling.
- Used by diagnostic, retry, block/tape, and HBA code.

Cautions:
- Fixed-format and descriptor-format sense must be detected before parsing.
- Variable-length descriptor data requires caller length validation.
