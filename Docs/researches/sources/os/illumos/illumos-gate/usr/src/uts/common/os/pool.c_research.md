# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pool.c

## Purpose

`pool.c` implements the common illumos resource pools layer: pool lifecycle, global pool state, pool locking, pool/resource association, pool property management, exacct packing for `/dev/pool`, process/project/task/zone pool binding, and asynchronous pool event callbacks.

Read completely: 1,797 lines.

## Main Responsibilities

- Initializes the default pool at boot and wires it to the default processor-set plugin.
- Provides long-duration, interruptible global pool locking with `pool_lock()`, `pool_lock_intr()`, `pool_unlock()`, and ownership checks through `pool_lock_held()`.
- Coordinates pool rebinding against fork, exec, exit, and LWP creation through the per-process pool barrier (`pool_barrier_enter()` / `pool_barrier_exit()`).
- Enables and disables the pools facility, including default system and pool properties, modification timestamps, and event dispatch.
- Creates/destroys pools and dispatches creation/destruction of pool resource components such as processor sets.
- Associates and disassociates pools with resource sets, currently processor sets via `pool_pset_assoc()`.
- Exposes pool configuration snapshots using exacct groups, including system, pool, and processor-set data.
- Validates and mutates system/pool/pset/CPU properties through typed `nvlist` property tables.
- Implements `pool_do_bind()`, the central atomic binding operation for PIDs, tasks, projects, pools, and zones.
- Provides async event callback registration and dispatch for pool enable/disable/change notifications.

## Important Data Structures And Globals

- `pool_default`: always-present default pool.
- `pool_count`, `pool_state`: current pool count and enabled/disabled state.
- `pool_buf` / `pool_bufsz`: saved pre-commit configuration snapshot used during pool commit transactions.
- `pool_sys_mod`, `pool_pool_mod`: system and pool modification timestamps reported in exacct output.
- `pool_sys_prop`: global pool-system property nvlist.
- `pool_ids`: ID allocator for non-default pools.
- `pool_list`: list of all `pool_t` objects.
- `pool_mutex`, `pool_busy_cv`, `pool_busy_thread`: implementation of the global pool lock.
- `pool_barrier_lock`, `pool_barrier_cv`, `pool_barrier_count`: synchronization with processes currently inside pool-sensitive barriers.
- `pool_event_cb_list`, `pool_event_cb_lock`, `pool_event_cb_taskq`: event callback registry and async delivery path.

## Control Flow And Algorithms

`pool_init()` allocates ID space, creates `pool_default`, initializes `pool_list`, initializes the processor-set plugin, assigns `p0` and the global zone to the default pool, and sets the default reference count.

`pool_status()` gates transitions. `POOL_ENABLED` initializes pset support and installs default system/pool properties; `POOL_DISABLED` refuses while more than one pool exists, disables pset support, and frees properties.

`pool_pool_create()` allocates a new `pool_t`, assigns an ID, attaches it to the default pset, initializes required properties, inserts it in `pool_list`, and increments `pool_count`. `pool_pool_destroy()` first rebinds all members to the default pool, updates zones that pointed at the destroyed pool, releases properties and ID allocation, updates pset pool counts, and frees the object.

`pool_pack_conf()` builds an exacct hierarchy by packing system metadata, pool records, and pset records. `pool_commit(1)` preserves a snapshot used by concurrent queries while a userspace commit is underway; `pool_commit(0)` releases that snapshot.

`pool_do_bind()` is the key atomic operation. It builds a target process list under `pidlock`, sets `PBWAIT`, waits for pool barriers to drain, rechecks exiting processes and newly forked children, performs pset preflight through `pset_bind_start()`, moves each process's threads to the target pset, optionally moves threads to a pool-specified scheduling class, updates `p_pool` references, wakes stopped processes, and finally handles project/zone cleanup. Failure before the binding phase wakes all stopped processes and leaves old bindings intact.

## Dependencies And Integration

- Calls into `pool_pset.c` for processor-set enable/disable/create/destroy/association/packing/property operations.
- Uses process, project, zone, scheduler, class, and FSS interfaces for binding semantics.
- Uses exacct and nvpair APIs for kernel-to-user configuration serialization.
- Integrates with `/dev/pool` ioctl paths and older pset/process binding callers through exported pool entry points.

## Locking And Concurrency

The file documents the lock order as `pool_lock() -> cpu_lock -> pidlock -> p_lock -> pool_barrier_lock`. The global pool lock is not a normal mutex because callers may sleep for long periods and may need signalable acquisition. Binding uses `PBWAIT` and `p_poolcnt` to stop relevant processes at stable points before rebinding their resource-set membership.

## Notable Risks And Invariants

- Callers must hold `pool_lock()` for almost all pool state mutation and snapshot operations.
- `pool_do_bind()` assumes resource-set-specific preflight and finish routines are kept in sync with operations that can make thread binding fail.
- Local zones cannot arbitrarily bind processes/tasks to pools; zone handling is deliberately constrained.
- Pool destruction requires every member to be rebound to the default pool and the destroyed pool reference count to drop to zero.
- Event callbacks are dispatched asynchronously and must not run while holding the pool lock.

## Research Relevance

This file is central to illumos workload/resource isolation. For filesystem and storage research it matters because pools influence scheduling, CPU placement, zones, project controls, and accounting context for kernel work and user processes that drive filesystem load.
