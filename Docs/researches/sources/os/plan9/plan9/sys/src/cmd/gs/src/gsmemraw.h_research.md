# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsmemraw.h

Legacy raw-memory allocator interface retained entirely inside `#if 0`. The comments explain that `gsmemraw` used to be an abstract base class but is no longer used; `gs_memory_t` is now the concrete base interface because the full interface is needed across the system.

The disabled content documents raw allocation semantics, alignment caveats, status reporting, stable allocators, `free_all`, consolidation, raw procedure tables, and `gs_raw_memory_s`. The active header only provides include guards, so it is documentation/compatibility residue rather than compiled API.
