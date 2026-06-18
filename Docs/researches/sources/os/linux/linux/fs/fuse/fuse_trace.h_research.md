# File Research: sources/os/linux/linux/fs/fuse/fuse_trace.h

Purpose: Defines FUSE tracepoints for request send and request completion.

Key responsibilities:
- Sets `TRACE_SYSTEM` to `fuse`.
- Defines the opcode symbolic table for FUSE and CUSE opcodes used by trace output.
- Emits `TRACE_DEFINE_ENUM()` entries for all listed opcodes.
- Defines `TRACE_EVENT(fuse_request_send)` with connection device id, unique request id, opcode, and input length.
- Defines `TRACE_EVENT(fuse_request_end)` with connection device id, unique request id, output length, and error code.
- Configures trace include path/file and includes `<trace/define_trace.h>`.

Important data/control flow:
- Tracepoints consume `struct fuse_req` fields from request headers and `req->fm->fc->dev`.
- Opcode names are generated from the same `OPCODES` macro table used for `__print_symbolic()`.

External dependencies:
- Linux tracepoint infrastructure.
- FUSE request structure from surrounding compilation context.

Notable edge cases:
- The opcode table includes both ordinary FUSE operations and `CUSE_INIT`.
- Trace output is diagnostic only and does not affect request lifecycle.
