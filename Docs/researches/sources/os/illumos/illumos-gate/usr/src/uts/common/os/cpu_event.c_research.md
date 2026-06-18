# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu_event.c

## Role

`cpu_event.c` implements the illumos CPU idle event notification framework. It lets kernel clients register callbacks that run just before a CPU enters a hardware idle state and just after it exits that state.

The implementation is optimized for the idle hot path: callback dispatch and property reads avoid normal locks, while registration and removal use `pause_cpus()` / `start_cpus()` to safely replace shared callback arrays.

## Main Concepts

The file defines two related facilities:

- CPU idle callbacks: ordered `idle_enter` and `idle_exit` callback functions registered by priority.
- CPU idle properties: per-CPU cache-aligned property storage exposed to callbacks through handles.

Built-in properties include:

- idle state
- enter timestamp
- exit timestamp
- last idle time
- last busy time
- total idle time
- total busy time
- interrupt count

Built-in callbacks include:

- DTrace idle-state transition probes.
- x86 non-XPV TLB idle service hooks, where available.

## Locking Strategy

The header comment documents the concurrency model:

- `cpu_idle_prop_busy` and `cpu_idle_prop_free` are protected by `cpu_idle_prop_lock`.
- `cpu_idle_cb_busy` is protected by `cpu_idle_cb_lock`.
- Per-CPU `cpu_idle_cb_state` does not need global locking.
- `cpu_idle_cb_array`, `cpu_idle_cb_curr`, and `cpu_idle_cb_max` are protected for writers by pausing other CPUs.
- The idle enter/exit hot path reads callback arrays without taking locks.

This design makes callback registration relatively expensive but idle transitions cheap.

## Initialization

`cpu_event_init()` initializes callback and property locks, creates internal properties, allocates cache-aligned per-CPU callback state for `max_ncpus`, caches property-value pointers in each per-CPU state record, and registers built-in callbacks.

`cpu_event_init_cpu()` enables per-CPU callback state when a CPU starts. `cpu_event_fini_cpu()` disables and clears per-CPU idle callback state when a CPU stops.

A notable implementation detail: the per-CPU state has an `intr_cnt` pointer field, but the initialization macro assigns the interrupt-count property to `last_idle` a second time. The file otherwise retrieves interrupt counts through property handles and update callbacks, so this cached field appears unused in the current implementation.

## Callback Registration

`cpu_idle_register_callback()` validates call context and parameters, rejects duplicate non-dynamic priorities, allocates a `cpu_idle_cb_impl_t`, inserts it into the busy list, and calls `cpu_idle_insert_callback()`.

`cpu_idle_insert_callback()` may allocate a larger callback array, then acquires `cpu_lock` if needed, pauses other CPUs if not already paused, swaps/copies the callback array, inserts the new callback item in priority order, resumes CPUs, and frees the old array.

`cpu_idle_unregister_callback()` validates that it is not called from an active callback, removes the implementation from the busy list, calls `cpu_idle_remove_callback()`, and frees the implementation.

`cpu_idle_remove_callback()` pauses CPUs, compacts the callback array, decrements the current count, and clears per-CPU property readiness when the last callback is removed.

## Idle Enter and Exit Flow

`cpu_idle_enter()` is called before entering hardware idle state. It:

- Resolves the current CPU callback context from `cpu_seqid`.
- Handles disabled per-CPU state.
- On x86, disables interrupts before callback dispatch.
- Updates idle state, enter timestamp, last busy time, and total busy time.
- Skips callbacks the first time a CPU’s idle state becomes ready.
- Calls registered `idle_enter` callbacks in priority order.
- Tracks `sp->v.index` so that `idle_exit` can unwind callbacks in reverse order.
- Detects interrupts or early exits during an enter callback by observing index changes and returns `EBUSY`.

`cpu_idle_exit()` is called after leaving hardware idle state. It:

- Updates idle state back to normal, exit timestamp, last idle time, and total idle time.
- Calls registered `idle_exit` callbacks in reverse order for only the callbacks whose enter side ran.
- Clears `sp->v.index`.
- Handles SPARC and x86 interrupt-state differences separately.

On x86, `cpu_idle_exit()` supports calls from either idle thread or interrupt handler. Interrupt-handler calls assume interrupts are already disabled; idle-thread calls disable and restore interrupts around exit processing.

## Idle Properties

`cpu_idle_prop_allocate_impl()` allocates property implementation records in groups sized to cache-line property groups and allocates cache-aligned per-CPU value storage.

Property APIs include:

- `cpu_idle_prop_create_property()`
- `cpu_idle_prop_destroy_property()`
- `cpu_idle_prop_create_handle()`
- `cpu_idle_prop_destroy_handle()`
- `cpu_idle_prop_get_type()`
- `cpu_idle_prop_get_name()`
- `cpu_idle_prop_get_value()`
- typed getters for `uint32`, `uint64`, `intptr`, and `hrtime`
- `cpu_idle_prop_set_value()`
- `cpu_idle_prop_set_all()`

Properties are reference-counted. Destroy succeeds only when the property has a single reference. Allocated backing value buffers are intentionally not freed individually.

`cpu_idle_prop_update_intr_cnt()` computes current interrupt count by summing per-PIL interrupt statistics on the current CPU.

## CPU State and x86 Poweroff Intercept

`cpu_idle_get_cpu_state()` returns the cached idle state for a CPU through the internal idle-state property.

On x86, `cpu_idle_intercept_cpu()` sets a bit in `cpu_idle_intercept_set`, pokes the target CPU, and waits until the target clears its bit inside `cpu_idle_enter()` with interrupts disabled. The target CPU then spins forever at a safe point before poweroff.

## DTrace Integration

The built-in DTrace callback emits `idle-state-transition` probes on idle enter and exit. Enter reports the requested idle state; exit reports the normal state.

## Research Notes

This file is a low-latency event framework tightly coupled to CPU idle paths. The critical invariants are no sleeping or unsafe locking on idle enter/exit, safe callback-array replacement using paused CPUs, correct reverse-order unwinding, and correct interrupt-state handling across architectures.
