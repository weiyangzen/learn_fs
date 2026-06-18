# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemsys.h

Interface between `jmemmgr.c` and platform-specific memory backends. No ordinary JPEG module should include it directly.

It declares backend hooks for small and large allocation, available-memory estimation, backing-store opening, and memory subsystem initialization/termination. It also defines `MAX_ALLOC_CHUNK`, defaulting to a large flat-memory value unless overridden by `jconfig.h`.

The central type is `backing_store_info`, which always carries read/write/close method pointers and then backend-private fields. DOS builds store a file/XMS/EMS handle union and temp name; Mac builds store a file reference, `FSSpec`, and name; ordinary builds store a `FILE *` and name.
