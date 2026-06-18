# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemsys.h

Purpose: interface between `jmemmgr.c` and platform-specific memory backends.

Key contents:
- Declares backend hooks for small allocation, large allocation, available-memory estimation, backing-store opening, memory initialization, and memory termination.
- Defines `MAX_ALLOC_CHUNK`, defaulting to a large flat-memory value unless overridden by `jconfig.h`.
- Defines `backing_store_info`, the common backing-store descriptor.

`backing_store_info` includes:
- `read_backing_store`
- `write_backing_store`
- `close_backing_store`
- Backend-private handle/name fields.

Backend-specific storage:
- DOS builds store a file/XMS/EMS handle union and temp name.
- Mac builds store a file reference, `FSSpec`, and name.
- Ordinary builds store a `FILE *` and temp name.

Notes:
- No ordinary JPEG module should include this directly; it is for the memory manager and backends.
