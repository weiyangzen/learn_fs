# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_pserialize.c

## Purpose
Implements passive serialization: very cheap read-side sections with an expensive write-side barrier that waits for all CPUs to pass a quiescent point.

## Main Entry Points
- `pserialize_init()` initializes global write-side locking.
- `pserialize_create()` and `pserialize_destroy()` allocate/free opaque passive serialization objects.
- `pserialize_perform()` performs the write-side synchronization barrier.
- `pserialize_read_enter()` and `pserialize_read_exit()` bracket read-side sections.
- `pserialize_in_read_section()` and `pserialize_not_in_read_section()` provide diagnostic predicates.

## Control Flow And State
The opaque `struct pserialize` currently contains only a dummy byte; serialization state is effectively global. Read enter raises to `splsoftserial()`, increments the current CPU's `ci_psz_read_depth`, and returns the previous priority for exit. Read exit asserts preemption is disabled in non-cold paths, decrements the depth with mismatch panic protection, and restores priority.

`pserialize_perform()` refuses interrupt/softint context, returns immediately during panic, counts an exclusive event directly when multiprocessor is not online, and otherwise issues a high-priority xcall barrier to all CPUs. It then briefly takes `psz_lock` to increment the event counter, serializing write-side accounting.

## Dependencies
Uses CPU per-CPU fields, SPL softserial, xcall barriers, kmem, mutexes, evcnt, panic/mp state, and LWP preemption counters.

## Risks And Notes
The API relies on read sections preventing preemption. `pserialize_not_in_read_section()` samples `lwp_pctr()` around the per-CPU depth check to account for context switches. Write-side barriers are intentionally expensive; frequent writers should use another synchronization primitive.
