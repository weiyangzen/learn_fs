# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/netstack.c

## Purpose

`netstack.c` is the illumos kernel framework for per-zone networking stack instances. It creates, reference-counts, shuts down, and destroys `netstack_t` objects, and lets networking modules register per-stack lifecycle callbacks.

Read completely: 1,456 lines.

## Main Responsibilities

- Registers with the zones framework through `zone_key_create()` so netstacks are created, shut down, and destroyed with zones.
- Maintains the global list of active and closing `netstack_t` objects.
- Supports shared global-stack zones and exclusive-IP zones.
- Provides module registration and unregistration through `netstack_register()` and `netstack_unregister()`.
- Runs module create callbacks in module-ID order and shutdown/destroy callbacks in reverse order.
- Provides lookup and hold/release entry points for current, credential, zone ID, and stack ID callers.
- Defers final netstack destruction to `system_taskq` to avoid teardown reentrancy.
- Keeps shared-stack kstats visible in every zone that uses the global/shared stack.

## Key State

- `netstack_g_lock` protects `ns_reg` and the `netstack_head` linked list.
- `ns_reg[NS_MAX]` stores module create, shutdown, destroy callbacks and module registration flags.
- `netstack_head` is the global list of netstacks, including closing objects that may still have references.
- `netstack_shared_lock` protects `netstack_shared_zones` and `netstack_shared_kstats`.
- `netstack_reap_limiter` caps outstanding deferred reaps; `netstack_outstanding_reaps` defaults to 1024.

Each `netstack_t` also has `netstack_lock`, `netstack_cv`, `netstack_refcnt`, `netstack_numzones`, `netstack_flags`, per-module `nm_state_t` flags, and module-private pointers.

## Lifecycle

`netstack_init()` initializes locks, the reap limiter, marks the subsystem initialized, and registers zone callbacks.

`netstack_zone_create()` maps a zone to either an exclusive stack ID or `GLOBAL_NETSTACKID`, reuses the global stack for shared zones, or allocates a new `netstack_t`. For new stacks it initializes per-module condition variables, marks needed create callbacks, runs `apply_all_modules(..., netstack_apply_create)`, then clears `NSF_UNINIT` and `NSF_ZONE_CREATE`.

`netstack_zone_shutdown()` only runs module shutdown callbacks when the last zone using a stack is shutting down. Shared-stack zones that are not the last user return without shutdown.

`netstack_zone_destroy()` decrements `netstack_numzones`. When the last zone is gone, it marks `NSF_CLOSING` so future lookups skip the stack and releases the zone-owned reference.

`netstack_rele()` decrements `netstack_refcnt` and dispatches `netstack_reap()` once both references and zone users reach zero. `netstack_reap()` calls `netstack_stack_inactive()`, unlinks the stack from `netstack_head`, destroys per-module CVs and stack locks, frees memory, and releases the reap limiter.

## Module Callback State Machine

Per-module state uses flags such as `NSS_CREATE_NEEDED`, `NSS_CREATE_INPROGRESS`, `NSS_CREATE_COMPLETED`, plus corresponding shutdown and destroy states.

`netstack_register()` installs callbacks under `netstack_g_lock`, marks create-needed on existing non-closing stacks, then calls `apply_all_netstacks()` to create module state everywhere.

`netstack_unregister()` marks shutdown and destroy needed for already-created module instances, sets `NRF_DYING` to prevent new creates, applies shutdown and destroy, then clears callback pointers and completed state.

`netstack_apply_create()`, `netstack_apply_shutdown()`, and `netstack_apply_destroy()` all wait for in-progress work on the same stack/module, set an in-progress flag, drop the outer lock while invoking callbacks, then record completion and broadcast the module CV.

## Ordering and Concurrency

The design is careful about concurrent zone creation, module loading, and module unloading:

- `wait_for_zone_creator()` makes `netstack_register()` and `netstack_unregister()` wait for a zone-created stack to finish create callbacks, preserving module-ID order.
- `wait_for_nms_inprogress()` serializes create, shutdown, and destroy work per stack/module.
- `apply_all_netstacks()` restarts from `netstack_head` whenever the callback drops `netstack_g_lock`, avoiding stale traversal after arbitrary list changes.
- Shutdown and destroy are applied in reverse module-ID order because module teardown may depend on create order.

## Lookup and Iteration

`netstack_get_current()` returns a held active stack from `curproc->p_zone->zone_netstack`. `netstack_find_by_cred()`, `netstack_find_by_zoneid()`, `netstack_find_by_zoneid_nolock()`, and `netstack_find_by_stackid()` locate a stack and hold it only if it is neither `NSF_UNINIT` nor `NSF_CLOSING`.

`netstack_next_init()`, `netstack_next()`, and `netstack_next_fini()` implement a simple held-object iterator over active stacks, skipping uninitialized and closing entries.

## Kstats and Shared Zones

`kstat_create_netstack()` creates zone-scoped kstats. For `GLOBAL_NETSTACKID`, it creates the kstat in the global zone and records it in `netstack_shared_kstats` so `kstat_zone_add()` can expose it to all shared-stack zones.

`netstack_shared_zone_add()` and `netstack_shared_zone_remove()` maintain the list of zones using the global stack and add or remove all shared-stack kstats from those zones. `zoneid_to_netstackid()` maps shared-stack zone IDs back to `GLOBAL_ZONEID`.

## Notable Invariants

- Exclusive-IP netstacks are not reused across zone reboot; the code relies on zones receiving new zone IDs.
- `netstack_find*()` callers must release returned stacks with `netstack_rele()`.
- Module create callbacks must return non-NULL module state.
- Final freeing is asynchronous because module data may have reentrant reference patterns.
- Shared-stack zone/kstat lists are maintained separately from the netstack list.

## Research Relevance

For filesystem and storage research, this file is mostly ambient OS infrastructure. It matters for zone-aware kernel services, kstat visibility, and networking-related storage protocols because it defines how per-zone network state outlives zones while references drain.
