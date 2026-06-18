# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/cpu.c

## Role

`cpu.c` is the architecture-independent CPU control core for illumos. It manages CPU topology lists, online/offline transitions, CPU hotplug configuration, processor binding, weak migration barriers, CPU pause coordination, CPU state reporting, processor-set/zone visibility, and CPU kstats.

It is the shared policy and synchronization layer above machine-dependent hooks such as `mp_cpu_start()`, `mp_cpu_stop()`, `mp_cpu_poweron()`, `mp_cpu_poweroff()`, `mp_cpu_configure()`, and interrupt enable/disable helpers.

## Global State and Locking

The central lock is `cpu_lock`, which protects `ncpus`, `ncpus_online`, `cpu_flag`, `cpu_list`, `cpu_active`, `cpu_active_set`, `cpu_available`, `cpu_seqid_inuse`, `cpu_seq`, `max_cpu_seqid_ever`, dispatch queue reallocations, and CPU topology mutations.

Important global structures include:

- `cpu_list`: circular list of all configured CPUs.
- `clock_cpu_list`: CPU list cursor used by clock code.
- `cpu_active`: circular list of online active CPUs.
- `cpu_active_set`: cached active CPU bitmap.
- `cpu_available`: configured CPU bitmap.
- `cpu_seq`: sequential CPU-id lookup table.
- `cpu_inmotion`: CPU currently being offlined or moved.
- `weakbindingbarrier`: global suppression flag for weak CPU bindings.
- `safe_list[]` and `cpu_pause_info`: cross-CPU quiesce/pause coordination.

The file repeatedly emphasizes a key invariant: some code walks CPU lists without `cpu_lock`, so list modifications are made while other CPUs are paused, and unlocked walkers must use preemption discipline and revalidation.

## CPU Affinity and Migration

`thread_affinity_set()` and `thread_affinity_clear()` implement counted hard CPU affinity. They support `CPU_CURRENT`, `CPU_BEST`, and explicit CPU IDs, update `t_bound_cpu`, and force migration or dispatch-queue movement through `force_thread_migrate()` when needed.

`thread_nomigrate()` and `thread_allowmigrate()` implement weak CPU affinity for short regions that must not migrate but should not fully disable preemption unless necessary. This is used for “no migration” semantics that are less disruptive than `kpreempt_disable()`.

Weak binding has careful interaction with CPU offline:

- `cpu_inmotion` marks an offline target so new weak bindings avoid that CPU.
- `weakbinding_stop()` forces future weak bindings to be satisfied by preemption disabling.
- Existing weak bindings are expected to drain quickly because callers must not block while weak-bound.
- Dispatcher behavior favors `t_weakbound_cpu` over strong binding while the weak binding exists.

## Pausing CPUs

The CPU pause subsystem creates high-priority per-CPU pause threads:

- `cpu_pause_alloc()` creates and binds a pause thread for a CPU.
- `cpu_pause_start()` schedules pause threads on all eligible CPUs except the caller/target.
- `pause_cpus()` waits until all selected CPUs reach a safe pause point, then raises interrupt priority on the current CPU.
- `start_cpus()` releases paused CPUs and restores the caller state.
- `cpu_pause_free()` safely kills a pause thread during CPU deletion.

The paused region is intentionally restrictive: code run while CPUs are paused must not acquire adaptive or low-level spin locks and must not block. This mechanism is fundamental to safe mutation of CPU global lists and hotplug state.

## CPU State Predicates

The file provides kernel-facing state tests that operate on `cpu_flags` while `cpu_lock` is held:

- `cpu_is_online()`
- `cpu_is_offline()`
- `cpu_is_poweredoff()`
- `cpu_is_nointr()`
- `cpu_is_active()`

The corresponding flag helpers are:

- `cpu_flagged_online()`
- `cpu_flagged_offline()`
- `cpu_flagged_poweredoff()`
- `cpu_flagged_nointr()`
- `cpu_flagged_active()`

User-visible processor states are derived separately by `cpu_flags_to_state()`, `cpu_get_state()`, and `cpu_get_state_str()`. The file explicitly separates internal `cpu_flags` semantics from `processor_info(2)` / `p_online(2)` states.

## Online, Offline, Fault, Spare, and Power Transitions

`cpu_online()` starts a CPU with `mp_cpu_start()`, inserts it into processor groups and active CPU lists while CPUs are paused, clears quiesced/offline/frozen/spare/fault/disabled flags, creates statistics and interrupt kstats, notifies CPU setup callbacks, enables interrupts, updates cyclic and callout subsystems, and pokes the CPU.

`cpu_offline()` is the most complex lifecycle transition. It:

- Rejects disabling the last online CPU in a partition or last interrupt-capable CPU.
- Unbinds soft or forced-bound user threads through `cpu_unbind()`.
- Notifies CPU state callbacks.
- Removes the CPU from processor groups.
- Disables interrupt participation through `cpu_intr_disable()`.
- Sets `cpu_inmotion` to discourage bindings and scheduling to the target CPU.
- Waits for bound threads to drain.
- Offlines callouts and cyclics.
- Calls `mp_cpu_stop()`.
- Pauses CPUs, removes the target from active lists, rehomes lgroup-affine threads, updates `t_cpu` for affected threads, marks `CPU_OFFLINE` and possibly `CPU_QUIESCED`, decrements `ncpus_online`, and tears down kstats.
- Rolls back interrupts, cyclics, callouts, processor group membership, and notifications if a later step fails.

`cpu_faulted()` and `cpu_spare()` layer on top of `cpu_offline()` or directly mark already-offline CPUs. `cpu_poweron()` and `cpu_poweroff()` delegate to machine-dependent power hooks and update visible state.

## CPU List and Hotplug Management

`cpu_list_init()` initializes the boot CPU’s circular lists, active set, partition membership, sequential ID, kmem cache offset, and CPU partition linkage.

`cpu_seq_tbl_init()` creates the dynamic sequential-ID table once memory allocation is available.

`cpu_add_unit()` adds a configured CPU to the all-CPU list and availability bitmap, assigns the first free sequential ID, initializes per-CPU cache offset, creates a pause thread, creates CPU info kstats, initializes machine-state accounting, and updates pool modification timestamps.

`cpu_del_unit()` removes an unconfigured CPU: it tears down processor-group and physical-ID state, destroys kstats and mstate accounting, frees the pause thread, removes availability and sequence mappings, pauses CPUs to unlink from `cpu_list`, marks the deleted CPU by nulling list pointers, decrements `ncpus`, and notifies lgroup/pool state.

`cpu_add_active_internal()` and `cpu_remove_active()` maintain the online active CPU list, per-partition circular list, active bitmap, processor-group state, lgroup state, partition CPU counts, and load-average state.

`cpu_configure()` and `cpu_unconfigure()` wrap machine-dependent CPU creation/destruction and invoke registered CPU setup hooks with rollback semantics.

## CPU Setup Callbacks

The file maintains a fixed-size `cpu_setups[]` callback table for early-boot feasibility. Callers register with `register_cpu_setup_func()` and unregister with `unregister_cpu_setup_func()`.

`cpu_state_change_notify()` broadcasts state changes without rollback. `cpu_state_change_hooks()` invokes callbacks and runs undo callbacks in reverse order if one fails.

Callbacks are called with `cpu_lock` held and must not block.

## CPU Kstats

The file exports CPU information and statistics through kstats:

- `cpu_info_kstat_create()` creates `cpu_info` named kstats.
- `cpu_info_kstat_update()` fills processor state, type, FPU type, MHz, chip/core IDs, implementation string, brand, current/supported frequencies, PG ID, SPARC FRU/device fields, and x86 vendor/family/model/cache/socket/C-state fields.
- `cpu_stats_kstat_create()` creates `cpu:<id>:sys`, `cpu:<id>:vm`, and raw `cpu_stat` kstats.
- `cpu_sys_stats_ks_update()` exports system counters and CPU mstate nanoseconds/ticks.
- `cpu_vm_stats_ks_update()` exports VM counters.
- `cpu_stat_ks_update()` exports legacy raw `cpu_stat_t` data.

The kstat update paths take care to avoid monotonic time counters moving backward by comparing current mstate values with previously exported values.

## Zone and Processor Set Visibility

When processor sets are enabled, CPU kstats are initially global-zone visible and then explicitly added to or removed from zones:

- `cpu_visibility_configure()`
- `cpu_visibility_online()`
- `cpu_visibility_add()`
- `cpu_visibility_offline()`
- `cpu_visibility_unconfigure()`
- `cpu_visibility_remove()`

These functions maintain `zone_ncpus`, `zone_ncpus_online`, and kstat zone visibility for `cpu_info`, `cpu_stat`, `cpu/sys`, `cpu/vm`, and `intrstat`.

## Processor Binding

`cpu_bind_thread()` implements per-thread processor binding semantics for `processor_bind(2)`-style operations. It supports query, query-type, soft/hard binding type changes, unbinding, explicit CPU binding, permission checks, partition checks, lgroup rehoming, dispatch queue movement, and `TP_CHANGEBIND` notification.

`cpu_unbind()` walks active processes under `pidlock` and unbinds threads bound to a target CPU, optionally skipping hard-bound threads unless forced.

`cpu_destroy_bound_threads()` removes remaining system-class bound threads for a CPU being destroyed, collecting them under `pidlock` and freeing them after dropping the lock.

## CPU Sets

The file implements allocation and operations for `cpuset_t`:

- Allocation/free: `cpuset_alloc()`, `cpuset_free()`.
- Initialization: `cpuset_all()`, `cpuset_all_but()`, `cpuset_only()`, `cpuset_zero()`.
- Membership: `cpu_in_set()`, `cpuset_add()`, `cpuset_del()`.
- Queries: `cpuset_isnull()`, `cpuset_isequal()`, `cpuset_find()`, `cpuset_bounds()`.
- Atomic mutation: `cpuset_atomic_add()`, `cpuset_atomic_del()`, `cpuset_atomic_xadd()`, `cpuset_atomic_xdel()`.
- Boolean operations: `cpuset_or()`, `cpuset_xor()`, `cpuset_and()`.

These are general kernel utilities but live here because CPU lifecycle state is a primary user.

## Frequency Reporting

`cpu_set_supp_freqs()` updates the string used by `cpu_info:supported_frequencies_Hz`. It allocates or replaces the per-CPU string and adjusts kstat data size under the kstat lock when the kstat already exists.

`cpu_set_curr_clock()` updates the current CPU frequency and fires the `cpu-change-speed` DTrace probe.

## Notable Dependencies

This file coordinates with many kernel subsystems:

- Dispatcher and thread migration.
- CPU partitions and processor sets.
- Locality groups.
- Processor groups and CMT topology.
- Cyclic subsystem and callouts.
- Interrupt routing.
- Kstats and zones.
- Power management through CPU state/frequency fields.
- Machine-dependent CPU bringup/offline/power hooks.

## Research Notes

This is a high-risk kernel coordination file. Changes must preserve lock ordering, pause-region restrictions, CPU lifecycle rollback, and dispatcher assumptions about active CPU lists. The CPU offline path is especially sensitive because it combines binding policy, interrupt routing, cyclic/callout state, lgroup rehoming, processor group state, and kstat visibility.
