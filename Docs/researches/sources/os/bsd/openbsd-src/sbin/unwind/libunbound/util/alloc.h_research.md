# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/util/alloc.h

`alloc.h` declares the allocation cache API and data structures. `alloc_special_type` is an alias for `struct ub_packed_rrset_key`; helper macros clean its ID and store freelist links in `entry.overflow_next`.

`struct alloc_cache` contains the optional super allocator pointer, a lock for top-level allocators, the special-object quarantine list/count, thread-number and ID range state, an ID-overflow cleanup callback, and cached regional arena state.

The public API initializes/clears caches, clears special objects, obtains/releases special RRset objects, allocates fresh IDs, reports memory/statistics, obtains/releases regional arenas, and installs the ID cleanup callback.

When `UNBOUND_ALLOC_LITE` is enabled, the header remaps `malloc`, `calloc`, `free`, `realloc`, `strdup`, selected sldns string conversion functions, `sldns_pkt2wire`, and `i2d_DSA_SIG` to checked wrappers implemented in `alloc.c`.
