<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-brk.c -->
# sources/test-tools/stress-ng/stress-brk.c

Purpose: `stress-brk.c` implements the `brk` VM/OS stressor. It rapidly grows, shrinks, resets, and partly unmaps the process data segment through `brk()` and `sbrk()`.

Important APIs/types/functions: `brk_context_t` stores shared counts, durations, byte limits, and options (`brk-mlock`, `brk-notouch`). `stress_brk_supported()` probes `sbrk(0)` and `brk(current)` for `ENOSYS`. `stress_brk_page_resident()` optionally touches the newest page and marks it mergeable. `stress_brk_child()` performs the actual page-by-page expand/shrink/reset/unmap loop and verifies a pointer check value at the end of pages. `stress_brk()` allocates shared context and wraps the child in `stress_oomable_child()`.

Control flow: top-level setup resolves options, syncs, then runs the OOM-able child. The child records the starting program break, optionally `mlockall(MCL_FUTURE)`, and loops through phases: reset when over the byte limit, shrink back toward start, avoid low memory if requested, expand by one page for several iterations, call `brk()` on the current position, shrink one page, verify the stored sentinel, and occasionally force-unmap a page from the brk region.

State and persistence behavior: no filesystem state is persisted. Process memory state is intentionally mutated through the program break and forced unmaps. Shared mmap state holds metrics visible to the parent after child completion.

Dependencies and integration points: integrates with stress-ng shim wrappers for `brk`/`sbrk`, anonymous shared mmap, OOM child control, memory-low checks, non-temporal load support, madvise, mlock, process states, options, and metrics.

Risks: manipulating the process break can interact badly with malloc or libraries if future changes allocate in the same child loop. Forced unmap inside the brk region is pathological by design and can expose kernel/libc assumptions. `brk-notouch` changes residency and can hide page-fault behavior.

Test signals: cover unsupported `sbrk`/`brk`, low `brk-bytes`, `brk-mlock`, `brk-notouch`, OOM-avoid behavior, and sentinel verification failures. Metrics are `nanosecs per sbrk page expand` and `nanosecs per sbrk page shrink`; debug logs count out-of-memory, expands, and shrinks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-brk.c -->
