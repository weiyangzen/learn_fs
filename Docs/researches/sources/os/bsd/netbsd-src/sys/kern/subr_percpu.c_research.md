# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_percpu.c

## Purpose
Implements dynamically allocated per-CPU storage with optional constructors/destructors, remote traversal, and xcall-based per-CPU callbacks.

## Main Entry Points
- `percpu_init()` creates the offset arena and global locks.
- `percpu_init_cpu()` allocates storage for a CPU and runs constructors for existing per-CPU objects.
- `percpu_alloc()`, `percpu_create()`, and `percpu_free()` allocate/free per-CPU regions.
- `percpu_getref()` and `percpu_putref()` access current-CPU data with preemption disabled.
- `percpu_traverse_enter()`, `percpu_traverse_exit()`, `percpu_getptr_remote()`, `percpu_foreach()`, and `percpu_foreach_xcall()` support remote traversal and callbacks.

## Control Flow And State
`struct percpu` records offset, size, optional ctor/dtor, cookie, and a list entry for objects with constructors. `percpu_offset_arena` hands out offsets; its import callback grows every CPU's `percpu_cpu_t` backing buffer. Growth allocates a new buffer per CPU and swaps it in via `percpu_cpu_swap()` locally or through an xcall, copying old data while interrupts are blocked so interrupt handlers cannot lose updates.

`percpu_swap_lock` protects stable remote traversal: growth takes it as writer, traversal as reader. Constructor list access is serialized by `percpu_allocation.lock`, `busy`, and `cv` so CPU initialization and new per-CPU object creation do not race while running callbacks.

## Dependencies
Uses kmem, vmem, CPU iteration, kernel preemption controls, rwlocks, mutexes/condition variables, and xcall infrastructure.

## Risks And Notes
Allocation/free are explicitly expensive and sleepable. Callback contracts matter: `percpu_foreach()` runs callbacks under the traversal lock on the current CPU and callbacks must be short and non-sleeping for allocations; `percpu_foreach_xcall()` runs in soft-interrupt context. Remote pointers are safe only inside traverse sections or when accessing the current CPU with preemption disabled.
