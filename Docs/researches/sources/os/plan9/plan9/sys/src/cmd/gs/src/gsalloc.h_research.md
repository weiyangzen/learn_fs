# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsalloc.h

Purpose: Declares extensions and internal hooks for the standard Ghostscript allocator.

Key interfaces: `gs_memory_gc_status_t`, GC status getters/setters, VM threshold/reclaim setters, allocator-state creation, controlled-chunk addition, GC preparation, reset functions, allocation-limit setup, and free-space consolidation.

Integration: Used by allocator users, GC, save/restore logic, and subsystems that need to adjust VM behavior.

Risks and notes: Exposes internal allocator lifecycle functions; misuse can break chunk/freelist/GC invariants.
