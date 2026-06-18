# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/rctl.c

## Purpose

Core kernel implementation of illumos resource controls (`rctl`). It lets subsystems register named controls, attach ordered control-value lists to process-model entities, enforce limits, translate legacy `rlimit` state, trigger actions, and maintain resource accounting for zone/project memory, swap, and lofi limits.

## Main Concepts

- Global dictionaries map resource-control handles and names to `rctl_dict_entry_t` definitions.
- Each controlled entity owns an `rctl_set_t` hash table of `rctl_t` instances keyed by handle.
- Each `rctl_t` has an ordered doubly linked list of `rctl_val_t` values plus an active `rc_cursor`.
- Ordering is by maximal flag, numeric value, deny action, privilege, and optionally action recipient.
- Controls apply to process, task, project, or zone entities.
- Project database values are cached separately in `rc_projdb` and synchronized with active `rc_values`.

## Key Entry Points

- `rctl_init()` creates caches, dictionaries, ID space, entity lists, and calls `rctlproc_init()`.
- `rctl_register()` registers a new named control, allocates its system value, assigns an ID, inserts global dictionary/list state, and panics on duplicate registration.
- `rctl_build_name_buf()`, `rctl_dict_lookup()`, `rctl_hndl_lookup()`, `rctl_dict_lookup_hndl()` expose lookup helpers.
- `rctl_set_create()`, `rctl_set_init_prealloc()`, `rctl_set_init()`, `rctl_set_dup_prealloc()`, `rctl_set_dup()`, `rctl_set_free()`, `rctl_set_reset()`, and `rctl_set_tearoff()` manage entity-local sets and fork/exec-style duplication.
- `rctl_local_get()`, `rctl_local_insert()`, `rctl_local_delete()`, `rctl_local_replace()`, `rctl_local_insert_all()`, and `rctl_local_replace_all()` implement local value mutation.
- `rctl_rlimit_get()`, `rctl_rlimit_set_prealloc()`, and `rctl_rlimit_set()` bridge POSIX-style soft/hard limits to resource-control values.
- `rctl_test()`, `rctl_test_entity()`, `rctl_action()`, and `rctl_action_entity()` perform enforcement and action delivery.
- `rctl_incr_locked_mem()`, `rctl_decr_locked_mem()`, `rctl_incr_swap()`, `rctl_decr_swap()`, `rctl_incr_lofi()`, and `rctl_decr_lofi()` charge and uncharge project/zone resources.
- `rctl_kstat_create_zone()`, `rctl_kstat_create_project()`, and `rctl_kstat_create_task()` create caps kstats.

## Locking and Allocation Model

- Documented lock order is `p_lock`, `rctl_dict_lock`, `rctl_lists_lock`, then `entity->rcs_lock`.
- The file avoids `KM_SLEEP` allocations while holding dictionary/list locks by using preallocation groups (`rctl_alloc_gp_t`) for set initialization, duplication, and rlimit mutation.
- `rctl_local_op()` requires `p_lock` and then locks the selected entity set.
- `rctl_local_action()` may drop `p_lock` and `rcs_lock` to allocate `sigqueue_t` or find a recipient process; it returns `RCT_LK_ABANDONED` so callers can reacquire and rewalk safely.
- Memory/resource charges use zone locks (`zone_mem_lock`, `zone_rctl_lock`) around accounting and rctl tests.

## Enforcement Behavior

- Global action logs exceeded controls through `strlog()` when `RCTL_GLOBAL_SYSLOG` is set and may force deny via `RCTL_GLOBAL_DENY_ALWAYS`.
- Local action can signal the violating process/thread or a registered recipient process and can deny operations for local deny actions.
- If an action does not deny and another value exists, enforcement advances `rc_cursor` to the next value and invokes the control's set callback.
- Kernel process `p0` is explicitly exempt from `rctl_test_entity()`.

## Dependencies

Uses kernel facilities including `mod_hash`, `id_space`, `kmem_cache`, process/task/project/zone structures, signals, credentials/policy, kstats, logging, and rctl ops vectors from subsystem registration files such as `rctl_proc.c`.

## Notes for Future Work

- Duplicate registration currently panics; the comments describe possible future unloadable-module support but it is not implemented here.
- The `rc_projdb` paths are sensitive to preallocation correctness because they intentionally mutate active and cached value lists under locks.
- Signal-recipient delivery has non-trivial lock dropping and entity membership revalidation; changes here should be tested against process exit, project/task movement, and unobservable controls.
