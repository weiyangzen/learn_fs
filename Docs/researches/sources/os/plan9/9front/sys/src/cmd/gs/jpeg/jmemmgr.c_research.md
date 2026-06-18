# File Research: sources/os/plan9/9front/sys/src/cmd/gs/jpeg/jmemmgr.c

Purpose: system-independent IJG memory manager.

Major responsibilities:
- Pool allocation.
- Chunked sample/block arrays.
- Virtual image arrays.
- Backing-store paging.
- Cleanup policy.

Important behavior:
- Keeps separate small and large allocation pools for `JPOOL_PERMANENT` and `JPOOL_IMAGE`.
- Small allocations are suballocated from slop-sized pools.
- Large allocations are one allocation per pool node.
- `alloc_sarray()` and `alloc_barray()` allocate row-pointer arrays plus chunked contiguous row storage while respecting `MAX_ALLOC_CHUNK`.
- Virtual arrays are first requested as control blocks, then realized once total demand is known.
- `realize_virt_arrays()` computes minimum and maximum memory needs, asks the backend through `jpeg_mem_available()`, assigns in-memory window heights, and opens backing store when full arrays do not fit.
- Virtual-array accessors page sample or block rows in and out, flush dirty buffers, pre-zero undefined rows when requested, and reject invalid access patterns.

Cleanup:
- `free_pool()` closes backing stores for image-lifetime virtual arrays before freeing large and small pools.
- `self_destruct()` frees all pools, releases the memory-manager object, and calls system-dependent termination.
- `jinit_memory_mgr()` validates alignment and allocation limits, initializes backend memory, installs the public method table, and honors `JPEGMEM` unless `NO_GETENV` is defined.

Dependencies:
- `jinclude.h`, `jpeglib.h`, `jmemsys.h`.
