# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/jpeg/jmemmgr.c

System-independent IJG memory manager. It provides pool allocation, chunked sample/block arrays, virtual image arrays, backing-store paging, and cleanup policy.

The manager keeps separate small and large allocation pools for `JPOOL_PERMANENT` and `JPOOL_IMAGE`. Small allocations are suballocated from slop-sized pools; large allocations are one allocation per pool node. `alloc_sarray()` and `alloc_barray()` allocate row-pointer arrays plus chunked contiguous row storage, respecting `MAX_ALLOC_CHUNK`.

Virtual arrays are requested as control blocks first, then realized later when total demand is known. `realize_virt_arrays()` computes minimum and maximum memory needs, asks the system backend via `jpeg_mem_available()`, assigns in-memory window heights, and opens backing store when full arrays do not fit. Accessors page sample or block rows in and out, flush dirty buffers, pre-zero undefined rows when requested, and reject invalid access patterns.

`free_pool()` closes backing stores for image-lifetime virtual arrays before freeing large and small pools. `self_destruct()` frees all pools, releases the memory-manager object, and calls system-dependent termination. `jinit_memory_mgr()` validates alignment and allocation limits, initializes backend memory, installs the public method table, and honors `JPEGMEM` unless `NO_GETENV` is defined.
