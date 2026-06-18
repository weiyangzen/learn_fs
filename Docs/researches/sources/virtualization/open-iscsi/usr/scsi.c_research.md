# File Research: sources/virtualization/open-iscsi/usr/scsi.c

Purpose: Provides SCSI sense-data normalization copied from Linux kernel SCSI error handling.

Key entry point:
- `scsi_normalize_sense(const uint8_t *sense_buffer, int sb_len, struct scsi_sense_hdr *sshdr)` extracts common fields from fixed-format and descriptor-format sense buffers.

Implementation notes:
- Rejects null or zero-length input, zeroes the output header, stores `response_code = sense_buffer[0] & 0x7f`, and validates it with `scsi_sense_valid()`.
- Descriptor-format responses (`response_code >= 0x72`) read `sense_key`, `asc`, `ascq`, and optional `additional_length` from bytes 1, 2, 3, and 7.
- Fixed-format responses read `sense_key` from byte 2 and, if the additional sense length covers them, read `asc` and `ascq` from bytes 12 and 13.
- The function returns 1 for valid normalized data and 0 when the sense buffer is absent or invalid.

Dependencies and interactions:
- Includes `scsi.h` for `struct scsi_sense_hdr` and `scsi_sense_valid()`.

Filesystem/storage relevance:
- Normalized sense keys and ASC/ASCQ values are the compact error details needed by storage tools when SCSI commands against iSCSI LUNs return CHECK CONDITION.
