# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsalloc.h

Purpose: Public/internal extension declarations for the standard Ghostscript allocator.

Exports: Defines `gs_memory_gc_status_t` with client-set GC threshold, max VM, signal pointer/value, enable flag, and allocator-set requested amount. Declares GC status getters/setters, VM threshold/reclaim setters, allocator-state allocation, controlled-chunk addition, GC preparation, reset, free-list reset, allocation-limit recompute, and free consolidation.

Dependencies and notes: Forward-declares `gs_ref_memory_t` when needed. The interface is lower-level than ordinary `gs_memory_t` allocation and is used by interpreter memory spaces and GC machinery.
