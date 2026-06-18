# sources/storage-engines/wiredtiger/src/cache/cache_pool.c

## Purpose

Implements the process-wide shared cache pool. Multiple WiredTiger connections in the same process can join a named pool, receive reserved/quota-based cache allocations, and have a manager thread rebalance `conn->cache_size` based on pressure and total pool capacity.

## Important APIs, Types, And Functions

Public entry points are `__wt_cache_pool_create` and `__wt_cache_pool_destroy`. Internal support includes `__cache_pool_config` for parsing/validating shared cache settings, `__conn_cache_pool_open` for joining the pool and starting a manager thread, `__cache_pool_server` as the per-connection manager thread loop, `__cache_pool_balance` as the locked rebalance pass, `__cache_pool_assess` for pressure scoring, and `__cache_pool_adjust` for growing/shrinking allocations.

The main state lives in global `__wt_process.cache_pool` (`WT_CACHE_POOL`), its spin locks/condition variable/refcount/connection queue, and per-connection cache fields such as `cp_reserved`, `cp_quota`, `cp_pass_pressure`, saved read/eviction counters, skip count, manager/run flags, `cp_session`, and `cp_tid`.

## Control Flow

Configuration rejects a shared-cache size without a name and rejects using both `cache_size` and `shared_cache`. It creates the singleton pool under the process spinlock or validates the requested name against the existing pool. It then locks the pool, increments refs for new joiners, resolves size/chunk/quota/reserve values from config or existing state, validates that all reserved allocations fit within pool size, stores pool/connection settings, and marks `WT_CONN_CACHE_POOL`.

Joining opens an internal no-data-handles session, inserts the connection into the pool queue, marks the pool active, sets the connection run flag, starts the manager thread, and signals for an initial allocation. Each manager thread loops while the pool and connection run flag are active. A CAS elects one active manager via `pool_managed`; that manager alternates forward/backward balancing passes.

Balancing first assesses pressure from bytes read, application eviction count, and application wait count, weighted by constants and cache size. Adjustment ensures each connection reaches its reserve, shrinks low-pressure or idle participants when the pool is full, and grows pressured participants when there is capacity and quota allows. Skip counters dampen oscillation after changes.

Destroying clears the connection cache-pool flag, removes the connection from the queue if present, returns its allocation to `currently_used`, stops and joins its manager thread, closes its internal session, decrements refs, and frees the singleton pool when the last participant exits.

## State And Persistence Behavior

The pool is process-local runtime state and does not persist across process restart. It mutates each participating connection's `cache_size`, which directly controls eviction thresholds and memory residency. Reserved and quota settings survive only as connection/cache fields. Destroy returns pool capacity and frees shared synchronization primitives after the last reference.

## Dependencies And Integration Points

This file integrates with WiredTiger global process state, config parsing, internal sessions, thread creation/join, condition variables, spin locks, eviction pressure helpers (`__wt_evict_needed` and `WT_EVICT` counters), cache byte accounting, verbose shared-cache logging, and `__wt_cache_config`, which decides whether the connection should enter or leave shared mode.

## Risks

Lock ordering is delicate: the process lock is dropped before acquiring the pool lock and reacquired in a documented order to avoid deadlock. Refcounts cover races between open/config and destroy. Rebalancing writes `entry->cache_size` while application/eviction threads read it, so allocation changes must be gradual and bounded. `cp_quota == 0` means unlimited for eligibility, but adjustment uses `cache->cp_quota - entry->cache_size`; implementations must preserve the intended zero-quota behavior. Error handling during partial pool creation or failed open must not leak the singleton, condition variable, or refcount.

## Test Signals

Signals include configuration validation errors for missing names, mixed `cache_size`/shared config, and reserve oversubscription; multi-connection tests showing initial reserve allocation, growth under read/eviction pressure, shrink when over budget, and quota enforcement; shutdown/reconfigure tests proving manager election handoff and clean singleton destruction; and stress tests around concurrent open/close/reconfigure with shared cache verbose logging enabled.
