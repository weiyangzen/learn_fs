# File Research: sources/os/bsd/openbsd-src/sbin/scsi/libscsi.c

This file provides a small userland SCSI request library: request allocation/reset, command/data format-string encoding and decoding, ioctl submission, and debug/sense dumping.

Key APIs:
- `scsireq_reset()`, `scsireq_new()`: initialize `scsireq_t` requests.
- `scsireq_build()`, `scsireq_build_visit()`: encode command descriptor blocks from a compact format grammar.
- `scsireq_encode_visit()`, `scsireq_buff_encode_visit()`: encode data buffers using callbacks.
- `scsireq_decode_visit()`, `scsireq_buff_decode_visit()`: decode buffers into callbacks or varargs.
- `scsi_open()`: opens a device and configures debug output from `SU_DEBUG_*` environment variables.
- `scsireq_enter()`: issues `SCIOCCOMMAND`.
- `scsi_debug()`, `scsi_dump()`: print command, data, status, and sense output.

Behavior and integration:
- Format grammars support integers, bit fields, char arrays, zero-trimmed char arrays, field names, assignment suppression, and seek controls.
- SCSI CDB/data values are encoded big-endian, matching SCSI specs.
- Sense decoding handles fixed-format `0x70`/`0x71` sense data and maps common sense keys/return statuses.
- Debug output can be redirected and truncated through environment variables.

Risk notes:
- Some APIs pass uninitialized `va_list` values when callback mode is intended; this is safe only as long as callers do not use the varargs path through those visit wrappers.
- `scsireq_build()` may allocate `databuf` internally and comments note this can leak.
- Encoding bounds checks are best-effort; tiny buffers and unusual widths depend on the caller providing sane lengths.
