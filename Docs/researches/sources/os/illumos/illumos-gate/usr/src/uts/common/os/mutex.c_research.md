# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/mutex.c

## Purpose

`mutex.c` implements illumos kernel mutual exclusion primitives for adaptive and spin mutexes. It provides the C slow paths behind assembly fast paths, lock initialization/destruction, ownership queries, adaptive blocking through turnstiles, spin-lock backoff, panic diagnostics, and lockstat instrumentation.

Read completely: 724 lines.

## Main Responsibilities

- Implements adaptive mutex acquisition slow path in `mutex_vector_enter()`.
- Implements spin mutex acquisition and tryenter slow paths.
- Implements contended/waiter-aware mutex release in `mutex_vector_exit()`.
- Provides `mutex_init()`, `mutex_destroy()`, `mutex_owned()`, and `mutex_owner()`.
- Implements default exponential randomized backoff and delay hooks.
- Implements simple spin-lock slow paths `lock_set_spin()` and `lock_set_spl_spin()`.
- Records lockstat events for spin, block, acquire, release, and destroy cases.

## Design Model

The file documents the mutex model in detail:

- Spin mutexes raise/block interrupts and spin until available; they are intended mainly for interrupt synchronization.
- Adaptive mutexes spin if the owner is running on another CPU and block otherwise.
- Fast-path `mutex_enter()` assumes adaptive layout; non-adaptive or held cases punt here.
- Blocking uses turnstiles and priority inheritance support.
- Adaptive mutex release wakes all waiters after clearing the lock and waiter state, avoiding direct handoff.

A key correctness issue is avoiding missed wakeups between `mutex_vector_enter()` setting the waiter bit and `mutex_exit()` clearing the owner without an atomic instruction. The implementation relies on platform trap/preemption fixups and carefully documented memory ordering.

## Key Data And Hooks

- `mutex_sobj_ops`: synchronization-object operations used by turnstile sleep.
- `panic_mutex` / `panic_mutex_addr`: first offending mutex snapshot for panic diagnostics.
- `mutex_backoff_base`, `mutex_backoff_cap`, `mutex_cap_factor`, `mutex_backoff_shift`: backoff tunables.
- `mutex_lock_backoff`, `mutex_lock_delay`, `mutex_delay`: function pointers for platform/default delay behavior.

## Acquisition And Release

`mutex_vector_enter()` handles spin locks by calling `lock_set_spl()`. For adaptive locks, it checks high-PIL misuse, records stats, repeatedly delays with backoff, tries to acquire unowned locks, detects recursion, spins while the owner is running, and blocks on a turnstile only after setting the waiter bit and rechecking state.

`mutex_vector_tryenter()` handles failed assembly tryenter cases. Adaptive locks have already been tried and return failure. Spin locks raise PIL, attempt `lock_try()`, store old PIL on success, and restore PIL on failure.

`mutex_vector_exit()` handles spin unlock via `lock_clear_splx()`. For adaptive locks, it verifies ownership, looks up the turnstile, atomically clears lock and waiter state through the macro path, wakes all writer waiters if any, and records release.

## Initialization And Destruction

`mutex_init()` chooses spin versus adaptive solely from the interrupt block cookie/PIL. PIL above `LOCK_LEVEL` creates a spin mutex with minimum SPL state; otherwise it creates an adaptive mutex. Optional alignment checking warns on unsupported unaligned mutex addresses.

`mutex_destroy()` permits destroying an unlocked mutex, destroying spin mutexes, or destroying an adaptive mutex held by the current thread with no waiters. It panics on bad type, non-owner destroy, or waiters.

## Spin Slow Paths

`lock_set_spin()` and `lock_set_spl_spin()` provide C fallback loops for contended spin locks. They panic on single-CPU deadlock scenarios, apply randomized exponential backoff, return early during panic, and record lockstat spin/acquire events. The SPL version temporarily drops to the old PIL while waiting, then raises again before retrying acquisition.

## Locking And Ordering Requirements

The top comment records external requirements:

- interrupt/trap code must restart preempted `mutex_exit()` critical regions,
- `resume()` must issue a store-load barrier after setting `CPU_THREAD`,
- `mutex_owner_running()` requires similar preemption fixup,
- idle threads cannot acquire adaptive locks.

These requirements are part of correctness, not just optimization.

## Notable Edge Cases

- Adaptive mutex acquisition at high PIL panics unless the system is already panicking.
- Recursive `mutex_enter()` panics.
- During panic, several paths return rather than spinning forever.
- `mutex_owned()` returns true during panic or quiesce.
- On single CPU, contended spin-lock slow paths panic because no other CPU can release the lock.
- Misaligned mutex warnings are capped to avoid log floods.

## Research Relevance

This file underpins synchronization throughout illumos, including VFS, device, and filesystem paths. Understanding its adaptive spin/block behavior and destruction rules is important when reasoning about storage-stack locking, deadlock risks, interrupt-level constraints, and performance under contention.
