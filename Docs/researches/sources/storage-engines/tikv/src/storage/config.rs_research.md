# sources/storage-engines/tikv/src/storage/config.rs

## Purpose

This module defines TiKV storage configuration, defaults, validation, API-version interpretation, flow-control settings, shared block-cache construction, IO-rate-limit construction, and max-ts safety settings.

## Important APIs, Types, And Functions

`EngineType` selects `RaftKv` or `RaftKv2` with a serde alias for `partitioned-raft-kv`. `Config` is an `OnlineConfig` structure containing data path, engine type, scheduler sizing, pending write and memory quotas, reserve space, async prewrite, API version and TTL flags, TTL polling, transaction status cache capacity, flow control, block cache, IO rate limit, background recovery window, and max-ts config.

`Config::validate_engine_type` canonicalizes data paths and resolves engine type from existing data directories. `Config::validate` clamps scheduler concurrency, validates API/TTL combinations, worker pool size, IO rate-limit mode, memory quota, and max-ts settings. `api_version` maps numeric config and TTL flag into `kvproto::kvrpcpb::ApiVersion`; `set_api_version` performs the reverse.

`FlowControlConfig::write_into_metrics` exports flow-control settings. `BlockCacheConfig::build_shared_cache` creates an LRU cache with adjusted shard bits, priority pool ratios, strict-capacity flag, and optional jemalloc nodump allocator. `IoRateLimitConfig::build` creates an `IoRateLimiter` and sets priorities for all IO types. `MaxTsConfig::validate` checks drift/cache-sync relation and invalid-update action.

## Control Flow

Default config derives scheduler worker pool size from CPU quota, using 8 workers for at least 16 cores and otherwise clamping between 1 and 4. Validation first resolves engine type against existing RocksDB or tablet data directories to avoid starting with an incompatible engine. It then checks scheduler, API, IO, memory, and max-ts invariants, mutating some values to safe bounds with warnings.

Block cache construction computes capacity from configured size or fallback, reduces shard bits when capacity cannot support the default shard count, attaches an allocator when requested and available, and creates a shared Rocks cache. IO rate-limit construction sets a global rate and all priority classes, while validation rejects unsupported modes and corrects unsafe `Other` and GC priorities.

## State And Persistence Behavior

This file defines configuration data, not runtime persistence. Validation mutates the in-memory config before use. Config persistence is handled by `ConfigController` outside this file. Built caches and IO limiters become runtime resources owned by database/server setup.

## Dependencies And Integration Points

It integrates `online_config`, RocksDB cache/resource options, filesystem IO limiter types, protobuf API version, global TiKV defaults for RocksDB/tablet subdirectories, CPU quota detection, and server flow-control metrics. `storage/config_manager.rs` applies the online portions to live components.

## Risks And Edge Cases

Existing data directories override configured engine type; if both v1 and v2 data directories exist, validation fails. API V2 requires TTL enabled. `scheduler_worker_pool_size` has a dynamic upper bound based on CPU quota. Block cache fallback exists for tests when TiKV config was not validated. Unsupported memory allocator names only warn and fall back. `MaxTsConfig` rejects a max drift less than or equal to cache sync interval to avoid stale max-ts decisions.

## Test Signals

Tests cover storage config validation, engine type resolution from existing data directories including the conflict case, and block-cache shard-bit adjustment across capacities.
