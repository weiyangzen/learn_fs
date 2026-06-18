# sources/storage-engines/tikv/src/storage/config_manager.rs

## Purpose

This module applies online storage configuration changes to live TiKV components: RocksDB/shared block cache, TTL checker worker, flow controller, transaction scheduler, IO rate limiter, and concurrency manager max-ts behavior.

## Important APIs, Types, And Functions

`StorageConfigManger<E, K, L>` stores a configurable database handle, TTL checker scheduler, flow controller, transaction scheduler, and concurrency manager. `new` wires those dependencies. The `ConfigManager` implementation provides `dispatch`, which consumes a `ConfigChange` and applies recognized changes.

## Control Flow

`dispatch` checks for known changes in priority order. For `block_cache.capacity`, it sets shared block cache capacity and updates the RocksDB CF metric. For `ttl_check_poll_interval`, it schedules `TtlCheckerTask::UpdatePollInterval`. For `flow_control`, it updates the flow controller config, toggles RocksDB `disable_write_stall` on all CFs when `enable` changes, and enables/disables the controller. For `scheduler_worker_pool_size`, it scales the scheduler pool. For `memory_quota`, it updates scheduler memory capacity. For `io_rate_limit`, it fetches the global limiter, applies max bytes per second, and iterates all `IoType` values to apply changed priorities. For `max_ts`, it updates invalid max-ts action and drift allowance in the concurrency manager.

## State And Persistence Behavior

All effects are in-memory runtime changes. Persistence of config files is handled before or around this manager by the online config controller. Some changes mutate external shared state immediately, including RocksDB options, scheduler pools, limiter settings, and concurrency-manager policy.

## Dependencies And Integration Points

The manager bridges `online_config`, TiKV `ConfigurableDb`, engine traits, filesystem global IO limiter, TTL worker scheduling, transaction scheduler, lock manager type parameters, flow controller, and concurrency manager. It relies on `ALL_CFS` and `CF_DEFAULT` for RocksDB CF updates and metrics.

## Risks And Edge Cases

The manager uses an `else if` chain for several top-level modules, so only the first matching branch among block cache, TTL interval, flow control, scheduler pool size, and memory quota is applied in that chain for a single `dispatch` call. IO rate limit and max-ts are handled afterward independently. Several runtime update calls use `unwrap`, so scheduling failure or CF config failure can panic. Missing global IO limiter returns an error. Priority conversion can fail and propagate.

## Test Signals

No local tests are present. Coverage should come from online config tests that update storage fields and assert side effects on scheduler, flow controller, IO limiter, and RocksDB options.
