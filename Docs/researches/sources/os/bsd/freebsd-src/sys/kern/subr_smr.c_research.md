# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_smr.c

## Purpose

`subr_smr.c` implements FreeBSD’s Safe Memory Reclamation mechanism based on Global Unbounded Sequences. It supports lockless reader sections and deferred reclamation by tracking sequence numbers observed by per-CPU readers and advancing a shared read sequence once all readers have observed a writer’s goal.

The design is intended to integrate with UMA so memory can be tagged on free and reused only after the required grace period.

## Algorithm Summary

The shared state has:

- A monotonic write sequence (`s_wr.seq`), initialized to an odd value.
- A shared read sequence (`s_rd_seq`) representing the lowest observed active reader sequence.
- Per-CPU reader sequence values (`c_seq`), with `SMR_SEQ_INVALID` meaning the CPU is outside an SMR read section.

Writers call `smr_advance()` to obtain a goal sequence. Reclamation waits or polls until `s_rd_seq` reaches that goal. Readers do not update global sequence state; they only record their observed sequence while inside read sections.

The algorithm handles wraparound with bounded deltas, odd valid sequence values, and invariant builds that deliberately force wrapping behavior for testing.

## Sequence Advancement Modes

`smr_shared_advance()` increments the shared write sequence by `SMR_SEQ_INCR`.

`smr_default_advance()` advances normal SMRs. It reads `s_rd_seq`, increments the write sequence, and if the writer gets too far ahead, calls `smr_wait()` to prevent undetectable wraparound. It updates debug counters.

`smr_lazy_advance()` advances lazy SMRs based on kernel ticks, with a two-tick grace window. This reduces write-side sequence churn and assumes periodic clock interrupts flush state sufficiently.

`smr_deferred_advance()` advances only after a per-CPU deferred counter reaches a configured limit. Before that, it returns a future goal relative to current shared state.

`smr_advance()` is the public entry. It asserts the caller is not inside the target SMR, issues a release fence so prior modifications are visible before sequence advancement, enters a critical section, chooses the correct advancement mode from per-CPU flags, and returns the goal.

## Polling

`smr_poll_cpu(c, s_rd_seq, goal, wait)` reads one CPU’s active sequence. Inactive CPUs immediately satisfy the poll. If a stale value below `s_rd_seq` is observed, it is pinned to `s_rd_seq` to handle races where a CPU loaded an older write sequence before publishing it. If `wait` is true, the function spins until the CPU observes the goal or exits.

`smr_poll_scan()` scans all CPUs, finds the minimum active sequence, and advances shared `s_rd_seq` if it observed progress.

`smr_poll(smr, goal, wait)` is the public poll/wait function. It rejects blocking waits from inside SMR sections and from lazy SMRs. It uses a critical section to avoid ABA races from long preemption sleeps, conditionally advances lazy/deferred write state, validates goal range, scans CPUs when needed, updates failure counters, and returns whether the goal has been observed. It issues an acquire fence before returning so subsequent reclamation sees readers’ memory effects.

## Lifecycle

`smr_create(name, limit, flags)` allocates shared state and per-CPU state from UMA zones, initializes shared read/write sequence numbers, initializes every CPU slot up to `mp_maxid`, and publishes with a seq-cst fence.

`smr_destroy(smr)` synchronizes, frees the shared state, and frees per-CPU state.

`smr_init()` creates UMA zones for shared and per-CPU SMR structures with cache-line alignment.

## Instrumentation

Debug sysctls under `debug.smr` expose counters for:

- `advance`
- `advance_wait`
- `poll`
- `poll_scan`
- `poll_fail`

These counters help identify workloads with expensive grace-period waits or failed nonblocking polls.

## Dependencies

The implementation depends on per-CPU UMA zones, counters, CPU iteration, SMP/critical sections, atomic ordering primitives, ticks, and definitions/macros from `sys/smr.h`.

## Maintenance Notes

Memory ordering is the core correctness property. The release fence in `smr_advance()`, acquire loads in polling, and acquire fence after polling are part of the reclamation contract. Changes to these paths must preserve the guarantee that memory freed before a goal is not reused until all pre-goal readers are gone or have observed the goal.

Lazy and deferred modes intentionally decouple writer progress from immediate global sequence increments. Callers must understand that nonblocking polls can fail until the relevant sequence is advanced.
