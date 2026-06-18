# sources/storage-engines/tikv/src/storage/kv/test_engine_builder.rs

## Purpose

This module provides `TestEngineBuilder`, a small builder for constructing temporary RocksDB-backed `RocksEngine` instances in tests with selectable path, column families, IO limiter, API version, and block-cache behavior.

## Important APIs, Types, And Functions

`TestEngineBuilder` fields are optional path, optional CF list, optional `IoRateLimiter`, and API version. Builder methods are `new`, `path`, `cfs`, `api_version`, `io_rate_limiter`, `build`, `build_with_cfg`, and `build_without_cache`. `do_build` creates CF options from `DbConfig`, `BlockCacheConfig`, shared CF resources, per-CF option builders, DB resources/options, and then opens `RocksEngine::new`.

## Control Flow

If no path is supplied, RocksDB receives the duplicated `TEMP_DIR` empty path default. If no CF list is supplied, all CFs are opened. `build_without_cache` sets block cache capacity to zero before constructing shared cache resources. Per-CF option creation handles default, lock, write, and raft CFs specially and falls back to default Rocks CF options for unknown names. Engine type is always `EngineType::RaftKv`.

## State And Persistence Behavior

The builder creates real RocksDB engine state at the supplied path or default temp path. Tests that pass a temp directory can close and reopen to verify persistence. The builder itself is consumed on build.

## Dependencies And Integration Points

It integrates RocksDB engine types, engine traits CF constants, filesystem IO limiter, protobuf API version, storage block-cache config, and the main TiKV `DbConfig` option builders. It is exposed through `storage::kv::TestEngineBuilder`.

## Risks And Edge Cases

The default path is an empty string duplicated from rocksdb_engine, so callers should pass explicit temp directories when isolation matters. The builder always uses `RaftKv` option paths even if tests request API V2; API version affects CF options but not engine type. Unknown CF names receive default CF options, which may not mimic production tuning.

## Test Signals

Tests verify base CRUD, linear behavior, CF statistics, reopen persistence, perf statistics, max-skippable-internal-keys error propagation, read perf delete-skip counters, and prefix-seek behavior around tombstones in the write CF.
