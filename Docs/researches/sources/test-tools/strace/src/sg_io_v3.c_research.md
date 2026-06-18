# sources/test-tools/strace/src/sg_io_v3.c

Purpose: MPERS-aware decoder for SCSI generic SG_IO v3 (`struct sg_io_hdr`) requests and responses.

Important APIs/types/functions: `print_sg_io_buffer`, `decode_request`, `decode_response`, `MPERS_PRINTER_DECL(decode_sg_io_v3)`, `struct_sg_io_hdr`, and xlat tables `sg_io_dxfer_direction`, `sg_io_flags`, and `sg_io_info`.

Control flow: entry prints interface id `'S'`, fetches the struct after the interface field, decodes direction, command buffer, sense-buffer length, iovec count, transfer length, timeout, flags, and outgoing data for TO_DEV/TO_FROM_DEV. It stores an entry copy in tcb private data. Exit fetches the completed struct, validates the interface id, prints incoming data adjusted by residual count, sense data, status fields, duration, residual, and info flags.

State and persistence behavior: stores an allocated entry-side `struct_sg_io_hdr` in tcb private data for exit decoding and fallback printing when the exit fetch fails.

Dependencies and integration points: requires `<scsi/sg.h>` for full decoding; otherwise prints a minimal `'S', ...` shell. Called from `scsi_ioctl` after SG_IO interface dispatch.

Risks: buffer lengths and iovec counts come from tracee memory; incorrect residual handling can overprint or underprint transfer data. MPERS pointer widths must match traced process layout.

Test signals: command-only, data-to-device, data-from-device, bidirectional transfer, iovec and flat buffers, nonzero residual, sense data, changed interface id, exit fetch failure, and builds without SCSI headers.
