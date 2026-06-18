# File Research: sources/os/linux/linux/fs/fuse/trace.c

Defines FUSE tracepoint storage for the tracepoint declarations in `fuse_trace.h`.

Key behavior:
- Includes `dev_uring_i.h`, `fuse_i.h`, `fuse_dev_i.h`, and `<linux/pagemap.h>`.
- Defines `CREATE_TRACE_POINTS` before including `fuse_trace.h`, causing the tracepoint definitions to be emitted in this translation unit.

Dependencies and integration:
- Pure trace infrastructure file; no runtime functions are declared here.
- Integrates FUSE core and io_uring/dev trace events into the kernel tracing subsystem.

Risks and invariants:
- Must remain the single translation unit defining `CREATE_TRACE_POINTS` for FUSE tracepoints to avoid duplicate definitions.
