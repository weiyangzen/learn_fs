# File Research: sources/os/linux/linux-stable/fs/ocfs2/dlm/dlmdomain.c

## Purpose

`dlmdomain.c` implements OCFS2 DLM domain lifecycle management: module initialization, domain allocation, domain join, protocol negotiation, heartbeat integration, network handler registration, domain leave, shutdown migration, and eviction callbacks.

A DLM domain is the cluster-wide context in which lock resources, master-list entries, recovery, ASTs, and network messages operate.

## Global State And Protocol

Global domain state:

- `dlm_domain_lock` protects `dlm_domains` and domain state transitions.
- `dlm_domains` tracks active domain contexts.
- `dlm_domain_events` wakes waiters during registration and teardown.

The supported DLM protocol is major `1`, minor `3`. The comments document additions in minor versions:

- `1.1`: heartbeat region query and nodeinfo query.
- `1.2`: begin-exit-domain message.
- `1.3`: deref-lockres-done message.

`dlm_protocol_compare()` requires equal major versions and negotiates down to the lower compatible minor version.

## Lock Resource Lookup

This file provides hash-table operations for lock resources:

- `__dlm_insert_lockres()`
- `__dlm_unhash_lockres()`
- `__dlm_lookup_lockres_full()`
- `__dlm_lookup_lockres()`
- `dlm_lookup_lockres()`

The “full” lookup returns resources even if they are dropping their master reference. The ordinary lookup filters out `DLM_LOCK_RES_DROPPING_REF`, which is suitable for most network handlers.

## Domain References

Domain lifetime is kref-based:

- `dlm_grab()` safely takes a reference only if the context is still in `dlm_domains`.
- `dlm_put()` releases a reference.
- `dlm_ctxt_release()` removes a failed or no-longer-joined context and frees memory.

`dlm_domain_fully_joined()` treats both `DLM_CTXT_JOINED` and `DLM_CTXT_IN_SHUTDOWN` as usable for message handling.

## Join Protocol

The join flow is implemented by:

- `dlm_try_to_join_domain()`
- `dlm_request_join()`
- `dlm_send_join_asserts()`
- `dlm_send_join_cancels()`
- handlers for query, assert, cancel, region, and nodeinfo messages.

Join requests are gated by:

- Heartbeat liveness.
- Existing domain state.
- Parallel join exclusion through `joining_node`.
- Recovery state.
- Node map consistency.
- DLM and filesystem protocol compatibility.
- Optional global heartbeat region matching.
- Node address/port consistency.

The join response is encoded as a packed four-byte packet carried as a `u32`, with endian conversion helpers to keep wire format consistent.

If all live nodes agree, the joining node builds `domain_map`, sends nodeinfo and heartbeat region queries when supported, asserts the join to peers, and transitions to `DLM_CTXT_JOINED`.

If maps change or a peer disallows the join, the join restarts with randomized short backoff, timing out after `DLM_JOIN_TIMEOUT_MSECS`.

## Leave And Shutdown

`dlm_unregister_domain()` decrements `num_joins`. On the last unregister it:

1. Marks the domain `DLM_CTXT_IN_SHUTDOWN`.
2. Sends begin-exit notifications for protocol 1.2+.
3. Kicks the DLM thread.
4. Repeatedly migrates or purges all lock resources via `dlm_migrate_all_locks()`.
5. Reports lock resources still on the tracking list.
6. Marks the domain `DLM_CTXT_LEAVING`.
7. Sends final exit-domain messages.
8. Force-frees remaining MLEs.
9. Completes DLM shutdown and removes the context from global lists.

`dlm_leave_domain()` clears the local node from `domain_map` and sends `DLM_EXIT_DOMAIN_MSG` until all peers are cleared or known unreachable.

## Domain Allocation

`dlm_alloc_ctxt()` allocates and initializes:

- Lock-resource and master hash page vectors.
- Debugfs subroot.
- Spinlocks and wait queues.
- Dirty, recovery, purge, handler, tracking, AST, BAST, MLE heartbeat, and work lists.
- Recovery state and node maps.
- MLE and lock-resource counters.
- Workqueue dispatch structure.
- Eviction callback list.

The initial state is `DLM_CTXT_NEW`.

## Message Handler Registration

`dlm_register_domain_handlers()` registers per-domain handlers keyed by the domain key for lock/resource operations, including master requests, assert master, create, convert, unlock, proxy AST, exit, deref, migration, recovery, and begin-exit messages.

`dlm_register_net_handlers()` registers global join-phase handlers using `DLM_MOD_KEY`.

Module init creates MLE, master, and lock caches, registers global net handlers, and creates the debugfs root. Module exit reverses this.

## Eviction Callbacks

The file provides exported callback APIs:

- `dlm_setup_eviction_cb()`
- `dlm_register_eviction_cb()`
- `dlm_unregister_eviction_cb()`

`dlm_fire_domain_eviction_callbacks()` invokes callbacks under a global rwsem. The comment explains why callbacks are needed before DLM recovery completes: the filesystem must know about node death before it can safely acquire recovery-sensitive locks.

## Concurrency

The file documents the DLM spinlock ordering:

1. `dlm_domain_lock`
2. `dlm_ctxt->spinlock`
3. `dlm_lock_resource->spinlock`
4. `dlm_ctxt->master_lock`
5. `dlm_ctxt->ast_lock`
6. `dlm_master_list_entry->spinlock`
7. `dlm_lock->spinlock`

Domain join and leave logic is careful to release locks around network sends and sleeps, then recheck state.
