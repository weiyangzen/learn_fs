# File Research: sources/virtualization/nbdkit/server/protocol.c

This file implements the post-handshake NBD request/reply data path. It reads request packets, validates commands, receives write payloads, dispatches backend operations under the request lock, and sends simple or structured replies.

`validate_request` enforces readonly restrictions, command-specific offset/count rules, valid range checks via `backend_valid_range`, valid flag combinations, advertised capability checks, maximum read/write request size, structured-reply requirements for DF and block status, and active `base:allocation` context for `NBD_CMD_BLOCK_STATUS`.

`handle_request` maps NBD commands to backend calls: `pread`, `pwrite`, `flush`, `trim`, `cache`, `zero`, and `extents`. It clears thread-local errno and last-error state before invoking plugins, translates NBD flags into nbdkit flags such as FUA, MAY_TRIM, FAST_ZERO, and REQ_ONE, and returns errno-style errors for conversion to NBD errors.

Reply handling supports simple replies for most operations and structured replies for reads and block status when negotiated. Structured reads send an offset-data chunk. Block-status replies translate `nbdkit_extents` into 32-bit NBD block descriptors, truncate lengths to protocol limits while preserving alignment, and send the negotiated `base_allocation_id`. Structured errors contain only the NBD error code, not a human-readable string.

Connection status gates the request loop. Client EOF and `NBD_CMD_DISC` mark client-done status, malformed requests or socket failures mark the connection dead, and server quit or inactive status returns `ESHUTDOWN`. Invalid write requests still drain the write payload when possible to keep the stream synchronized before sending an error.
