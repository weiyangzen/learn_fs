# File Research: sources/os/bsd/dragonflybsd/sys/sys/usched_dfly.h

## Summary
DragonFly scheduler priority, runqueue, and per-CPU scheduler data definitions.

## Main Responsibilities
- Defines priority bands, runqueue counts, priority-per-queue math, nice/estcpu scaling, and estcpu limits.
- Maps generic LWP scheduler data fields to DragonFly-specific names.
- Provides `lptouload()` for estimated per-LWP scheduler load.
- Defines `struct usched_dfly_pcpu` with spinlock, helper thread, queues, queue bitmaps, run count, CPU identity, CPU mask, and topology node.
- Defines per-CPU mask reflection flags.

## Important Behavior
The scheduler uses 32 queues per class, with four priority levels per queue. `uload` is long-sized specifically to avoid overflow on very large process counts.

## Risks
This header assumes access to `struct lwp`, process nice values, cpumasks, and globaldata. Queue bitmap and priority math must remain synchronized with scheduler implementation code.
