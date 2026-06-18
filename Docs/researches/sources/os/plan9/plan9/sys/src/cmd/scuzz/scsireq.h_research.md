# File Research: sources/os/plan9/plan9/sys/src/cmd/scuzz/scsireq.h

Shared SCSI request definitions.

Key contents:
- Defines `ScsiPtr` and `ScsiReq`, including unit path, lun, block size, offset, fd, command/data buffers, status, sense, inquiry, and flags.
- Defines software flags for device type/state, raw USB routing, 6-byte mode select, and 10-byte read/write.
- Defines SCSI status constants and internal status values.
- Defines sense-data bit masks and big-endian get/put macros.
- Declares all request helpers from `scsireq.c`, CD audio, CD-R, changer, and sense modules.

Important details:
- Header notes it is also included by USB disk and CDFS code.
- `Max24off` limits 24-bit command offsets.
- `maxiosize` is extern and shared with `scuzz.c`.

Filesystem relevance:
- Indirect but central to raw block/media device access in the scuzz subsystem.
