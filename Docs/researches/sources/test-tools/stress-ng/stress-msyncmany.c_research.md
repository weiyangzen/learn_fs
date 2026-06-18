# sources/test-tools/stress-ng/stress-msyncmany.c

Purpose: implements `msyncmany`, a VM stressor that maps the same single-page file many times, writes through one mapping, syncs and invalidates it, and verifies all aliases observe the same value.

Important APIs/types/functions: `stress_msyncmany()` creates an unlinked temp file and allocates one page. `stress_msyncmany_child()` maps the file repeatedly up to `_SC_MAPPED_FILES` capped by `MMAP_MAX`, stores mapping pointers, and performs the sync/alias verification loop under OOM handling.

Control flow: the parent creates a temp directory/file, unlinks the file, `fallocate()`s one page, then runs the child through `stress_oomable_child()`. The child allocates a mapping table, creates as many `MAP_SHARED` one-page mappings of fd offset zero as possible, synchronizes, writes a random pattern through the first mapping, calls `msync(MS_SYNC | MS_INVALIDATE)`, verifies every mapping reads the same pattern, and increments bogo operations. Cleanup unmaps all mappings, closes the inherited fd, and frees the table.

State and persistence: persistent state is the unlinked one-page file descriptor and the child mapping table. Temp directory and file descriptor are cleaned by parent and child paths; mappings are transient.

Dependencies and integration: requires `msync()`; uses temp-file helpers, `fallocate`, OOM wrapper, memory-low checks, VMA naming, and stress-ng synchronization.

Risks and test signals: VMA limits or low memory can prevent mappings, and alias coherence bugs show as mismatched patterns. Good signals are nonzero mapping count, successful `MS_SYNC | MS_INVALIDATE`, no more than a few verification failures before abort, and complete unmap/close cleanup.
