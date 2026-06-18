# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsnogc.c

Implements a non-tracing “ersatz GC” for environments that do not need full garbage collection or save/restore. It focuses on string freelists and free-space consolidation.

`sf_alloc_string` searches the current chunk’s large-string freelist for exact-size matches. `sf_free_string` returns strings either by moving `ctop` when freeing the top string, by inserting large strings into an address-ordered freelist, or by adding tiny strings to 1-byte freelists per 256-byte block. Debug checks detect overlapping frees.

`sf_consolidate_free` closes the current chunk, merges free strings at the bottom of string storage, can recover string-marking-table space when no string space is used, reopens the chunk, and then consolidates object free space. `gs_nogc_reclaim` installs these string-freelist procedures on all VM spaces and stable memories, then consolidates.

This is reclamation without tracing: it coalesces allocator-managed free regions but does not discover unreachable live objects.
