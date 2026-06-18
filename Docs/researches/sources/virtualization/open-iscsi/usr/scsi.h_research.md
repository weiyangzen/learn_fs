# File Research: sources/virtualization/open-iscsi/usr/scsi.h

Purpose: Declares the SCSI sense header abstraction and normalization API.

Key definitions:
- `struct scsi_sense_hdr` stores response code, sense key, ASC, ASCQ, three intermediate bytes, and descriptor-format additional length.
- `scsi_sense_valid()` returns true when the response code has the SCSI sense response class bits (`0x70`) set.
- `scsi_normalize_sense()` is declared for converting raw sense bytes into `struct scsi_sense_hdr`.

Implementation notes:
- The structure intentionally supports response codes `0x70`, `0x71`, `0x72`, and `0x73`, allowing both fixed and descriptor sense formats to be represented in one shape.

Dependencies and interactions:
- Includes `stdint.h` for fixed-width byte fields.

Filesystem/storage relevance:
- Defines the minimal SCSI error-information structure used by initiator-side storage diagnostics and error handling.
