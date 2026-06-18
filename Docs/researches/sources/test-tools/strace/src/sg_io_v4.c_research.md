# sources/test-tools/strace/src/sg_io_v4.c

Purpose: decoder for SG_IO v4 / block SCSI generic (`struct sg_io_v4`) requests and responses.

Important APIs/types/functions: `print_sg_io_buffer`, `decode_request`, `decode_response`, `decode_sg_io_v4`, and xlat tables `bsg_protocol`, `bsg_subprotocol`, `bsg_flags`, and shared `sg_io_info`.

Control flow: entry prints guard `'Q'`, protocol/subprotocol, request buffer, request metadata, response maximum length, dout/din iovec counts and lengths, outgoing transfer buffer, timeout, flags, and user pointer; it stores an entry copy. Exit fetches the result struct, validates guard, prints response bytes, incoming data adjusted by `din_resid`, driver/transport/device status, retry delay, info, duration, residuals, and generated tag.

State and persistence behavior: uses tcb private data to retain entry-side addresses and sizes for exit fallback and guard validation.

Dependencies and integration points: uses Linux `<linux/bsg.h>`, generic print/iovec helpers, and is selected by `scsi_ioctl` when the SG_IO interface id is `'Q'`.

Risks: response length is printed twice in the current flow, matching source behavior but worth testing for golden output stability. Residual and iovec length calculations need coverage to avoid reading beyond returned data.

Test signals: v4 requests with request/response buffers, dout and din transfers, iovec paths, residual truncation, guard mismatch, unreadable exit struct, and flag/protocol xlat output.
