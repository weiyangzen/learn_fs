<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v4.c -->
# sources/test-tools/strace/tests/ioctl_sg_io_v4.c

Purpose: tests SCSI generic `SG_IO` v4 (`struct sg_io_v4`) decoding used by block SCSI generic interfaces.

Important APIs/types/functions: Uses `linux/bsg.h`, `struct sg_io_v4`, `SG_IO`, protocol/subprotocol fields, request/response/dout/din pointers, iovec counts, flags, info, durations, residual fields, and SCSI xlat command support.

Control flow: probes NULL, EFAULT, invalid guard, partial guard, then valid guard `'Q'` with crafted protocol, subprotocol, request/response pointers, iovec/direct transfer buffers, dout/din transfer lengths, residuals, flags, status, and info fields.

State and persistence behavior: local v4 header and buffers only; invalid fd prevents real SCSI I/O.

Dependencies/integration points: validates strace SG_IO v4 decoder against Linux BSG UAPI and iovec printing helpers.

Risks and test signals: struct layout and flags are header-sensitive. Passing output confirms guard/protocol decoding, request/response pointer fields, bidirectional transfer formatting, residual handling, and flags/info expansion.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioctl_sg_io_v4.c -->
