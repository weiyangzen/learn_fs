# File Research: sources/os/linux/linux-stable/fs/fuse/fuse_trace.h

## Purpose

`fuse_trace.h` defines FUSE tracepoints for request submission and completion. It provides symbolic opcode names and trace event layouts used by Linux ftrace/perf tooling.

## Main Responsibilities

- Defines an `OPCODES` macro table mapping FUSE/CUSE opcode constants to printable names.
- Emits `TRACE_DEFINE_ENUM()` entries for each opcode.
- Reuses the opcode table for `__print_symbolic()`.
- Defines `fuse_request_send` trace event.
- Defines `fuse_request_end` trace event.
- Sets `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and includes `trace/define_trace.h`.

## Trace Events

`fuse_request_send` records:
- connection device id,
- request unique id,
- opcode,
- input header length,
- symbolic opcode name.

`fuse_request_end` records:
- connection device id,
- request unique id,
- output header length,
- request error code.

## Dependencies

The tracepoints consume `struct fuse_req` fields:
- `req->fm->fc->dev`
- `req->in.h.unique`
- `req->in.h.opcode`
- `req->in.h.len`
- `req->out.h.len`
- `req->out.h.error`

## Notes

The opcode table includes standard FUSE operations, newer operations such as `FUSE_TMPFILE` and `FUSE_STATX`, DAX mapping operations, syncfs, and `CUSE_INIT`.
