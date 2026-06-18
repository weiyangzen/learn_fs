# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cyclic.c

## Purpose

`cyclic.c` implements the illumos cyclic subsystem: high-resolution, per-CPU interval timers that can fire at high, lock, or low interrupt level. It is the kernel’s low-level timer engine for recurring and reprogrammable callbacks, including CPU-bound, CPU-partition-bound, and omnipresent timers.

The file is unusually well documented. Its design centers on minimizing cross-CPU interference by keeping timer state in per-CPU `cyc_cpu_t` structures and using a heap ordered by absolute expiration time.

## Core Data Model

Each CPU owns:

- `cyp_cyclics`: an expandable array of `cyclic_t` slots.
- `cyp_heap`: an array heap of cyclic indexes, sorted by `cy_expire`.
- `cyp_softbuf[]`: producer/consumer buffers for lock-level and low-level cyclics.
- `cyp_state`: online/offline/suspended/expanding/removing state.
- backend state copied from the platform `cyc_backend_t`.

Cyclic IDs are represented by `cyc_id_t`, not opaque numeric handles. Regular IDs point to a single CPU/index pair. Omnipresent IDs keep a linked list of `cyc_omni_cpu_t` components, one per online CPU.

## Timer Firing

`cyclic_fire()` is the high-level interrupt entry point called by the platform backend. It:

- Reads the current high-resolution time.
- Checks the heap root.
- Expires root cyclics whose `cy_expire <= now`.
- Recomputes the next expiration from the previous expiration plus interval.
- Handles `CY_INFINITY` as a one-shot/reprogrammable timer pattern.
- Corrects very late expirations by jumping to the next interval boundary.
- Downheaps after each expiration.
- Reprograms the backend with the next root expiration.

`cyclic_expire()` either calls high-level handlers directly or enqueues lower-level handlers into the appropriate soft interrupt producer/consumer buffer and posts a backend soft interrupt.

## Soft Interrupt Handling

`cyclic_softint()` drains pending lock-level or low-level cyclics. Pending work is tracked with `cy_pend`, which counts how many handler invocations are owed. The softint path calls the handler before atomically decrementing `cy_pend`, preserving the one-to-one mapping between high-level expirations and low-level handler calls.

The implementation is mostly lock-free on the hot path. It handles three difficult races explicitly:

- New high-level expirations bumping `cy_pend` while softint drains it.
- Per-CPU array resize while a softint holds an old `cyp_cyclics` pointer.
- Cyclic removal while a softint is executing or about to execute the handler.

Removal with pending callbacks uses `cyp_rpend` and `cyclic_remove_pend()` so `cyclic_remove()` can preserve the guarantee that all owed handler calls complete before removal returns.

## Heap And Resizing

`cyclic_upheap()` and `cyclic_downheap()` maintain the per-CPU min-heap by expiration time. The heap stores indexes into `cyp_cyclics`, allowing compact arrays and cache-local heap operations.

`cyclic_expand()` doubles the per-CPU heap, cyclic array, and soft buffers. It cross-calls the target CPU through `cyclic_expand_xcall()`, switches heap/cyclic pointers at high interrupt level, zeroes old `cy_pend` values to force softint retry against the new array, flips hard producer buffers, then waits for both soft levels to observe the new buffers before freeing old storage.

## Add, Remove, And Reprogram

`cyclic_add()` creates a regular cyclic under `cpu_lock`, chooses a suitable CPU with `cyclic_pick_cpu()`, allocates a `cyc_id_t`, and inserts the cyclic on the target CPU via cross-call.

`cyclic_remove()` removes either a regular cyclic or all components of an omnipresent cyclic. Regular removal uses `cyclic_remove_here()` and `cyclic_remove_xcall()` to remove the cyclic from its CPU heap at high level, disable the backend if the CPU heap becomes empty, and wait for pending low-level callbacks if required.

`cyclic_reprogram()` can be called from a cyclic handler. It uses `cyi_lock` as a reader lock to prevent migration/removal while reprogramming. Local reprogramming calls `cyclic_reprogram_cyclic()` directly at high level; remote reprogramming cross-calls the owning CPU. A local handler racing with removal may get a failure return instead of a panic.

## CPU Mobility

The file integrates tightly with CPU management:

- `cyclic_juggle()` moves movable cyclics away from a CPU.
- `cyclic_offline()` juggles regular cyclics away and stops omnipresent components.
- `cyclic_online()` restarts omnipresent cyclics on the CPU.
- `cyclic_move_in()` and `cyclic_move_out()` handle CPU partition transitions.
- `cyclic_bind()` applies CPU and CPU-partition bindings.
- `cyclic_move_here()` best-effort migrates an unbound cyclic to the current CPU.

Migration removes the cyclic from the source CPU while preserving its expiration time, then re-adds it to the destination CPU. This relies on `gethrtime()` increasing consistently across CPUs.

## Suspend And Backend Integration

`cyclic_init()` installs the backend template, configures CPU 0, and onlines it. `cyclic_mp_init()` configures remaining CPUs and registers CPU setup hooks.

`cyclic_suspend()` cross-calls every CPU and disables active backends while preserving per-CPU state. `cyclic_resume()` resumes backends, reenables CPUs with cyclics, and reprograms each backend from its heap root.

The backend contract is abstracted through `cyb_configure`, `cyb_enable`, `cyb_disable`, `cyb_reprogram`, `cyb_softint`, `cyb_xcall`, `cyb_set_level`, `cyb_restore_level`, `cyb_suspend`, and `cyb_resume`.

## Dependencies

Key dependencies include:

- CPU lifecycle and partition state: `cpu_lock`, `cpu_t`, `cpupart_t`, CPU flags.
- High-resolution time: `gethrtime()`, `gethrtime_unscaled()`.
- Interrupt/cross-call backend APIs from `cyc_backend_t`.
- Synchronization primitives: semaphores, reader-writer locks, atomics, preemption disable.
- Kernel memory allocation and DTrace probes.

## Research Notes

This file is a concurrency-heavy kernel subsystem. Highest-risk areas are softint resize/removal races, `cy_pend` accounting, backend reprogramming after heap root changes, migration while preserving single-threaded handler semantics, and reprogramming from within handlers racing with removal or omnipresent CPU offline.
