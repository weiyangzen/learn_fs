# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pg.c

## Purpose

`pg.c` implements the generic processor group framework. Processor groups model logical or physical relationships among CPUs and provide class-specific hooks for scheduler topology, CPU lifecycle, CPU partition movement, and dispatcher thread-switch events.

Read completely: 828 lines.

## Main Responsibilities

- Registers processor group classes.
- Allocates and destroys generic `pg_t` objects with sequential PG IDs.
- Maintains CPU membership in PGs and PG membership in per-CPU `cpu_pg_t` data.
- Initializes and tears down per-CPU processor group state.
- Broadcasts CPU active/inactive and CPU partition callbacks to all classes.
- Provides default allocation, free, and callback operations.
- Invokes per-PG dispatcher callbacks on thread switch and thread remain events.

## Class Model

`pg_class_register()` appends a `pg_class_t` to the global class array under `cpu_lock`. Each class has a name, ID, operations table, and relation type such as `PGR_LOGICAL` or physical relations used by CMT.

Default operations are `pg_alloc_default()`, `pg_free_default()`, and null event callbacks. Class-specific callbacks may override allocation, CPU init/fini, active/inactive, CPU partition in/out/move, membership testing, and policy naming.

`pg_init()` registers the default class, initializes the CMT class through `pg_cmt_class_init()`, initializes CPU0, and starts CMT CPU startup for the boot CPU.

## PG Creation and Membership

`pg_create()` allocates a PG through the class allocator, assigns class and relation fields, finds the next free sequential PG ID using `pg_id_set`, creates the PG CPU group, and installs default event callbacks.

`pg_destroy()` destroys the CPU group, releases the PG ID, updates `pg_id_next`, and frees the PG through the class free operation.

`pg_cpu_add()` adds a CPU to the PG's CPU group and adds the PG to the CPU's pending `cpu_pg_t` group. `pg_cpu_delete()` removes both links. Both require `cpu_lock` and assert that the CPU is still using bootstrap PG data because the routines may block.

`pg_cpu_find_pg()`, `pg_cpu_next()`, and `pg_cpu_find()` provide class membership and iteration helpers.

## Per-CPU PG Data

`pg_cpu_data_alloc()` creates `cpu_pg_t` and initializes `pgs` and `cmt_pgs` groups. `pg_cpu_data_free()` destroys those groups and frees the object.

`pg_cpu_init()` allocates CPU PG data and calls every class `cpu_init` callback. Unless deferred, it installs the new data into `cp->cpu_pg`.

`pg_cpu_fini()` switches the CPU back to bootstrap data if needed, calls every class `cpu_fini`, and frees the old data.

`pg_cpu_bootstrap()` points a CPU at the static `bootstrap_pg_data`; `pg_cpu_is_bootstrapped()` tests that state. This protects code that may see a partially initialized CPU.

## CPU and Partition Events

All event entry points require `cpu_lock`:

- `pg_cpu_active()` and `pg_cpu_inactive()` notify classes when CPUs come online or go offline. They may not block because they are called from paused CPU context.
- `pg_cpupart_in()` and `pg_cpupart_out()` notify classes before CPU partition entry or exit and may block.
- `pg_cpupart_move()` notifies classes during a CPU partition move and may not block.
- `pg_cpu0_reinit()` tears down and rebuilds CPU0 PG data after topology changes.

## Dispatcher Event Callbacks

`pg_ev_thread_swtch()` iterates all PGs for the CPU and calls each PG's `thread_swtch` callback with timestamp, old thread, and new thread.

`pg_ev_thread_remain()` calls each PG's `thread_remain` callback when a thread switches to itself after a timeslice artifact.

## Notable Invariants

- Most structural mutations require `cpu_lock`.
- Active/inactive and partition move callbacks must not block.
- CPU PG data construction uses bootstrap indirection to survive blocking allocations and dispatcher entry.
- PG class-specific views are expected to embed `pg_t` first.

## Research Relevance

This file matters for scheduler and CPU-topology context around filesystem workloads. It does not implement filesystem behavior, but it defines the CPU grouping callbacks used by load balancing, CMT locality, and hardware-sharing policy.
