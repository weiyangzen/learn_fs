# sources/storage-engines/tikv/src/server/ttl/ttl_compaction_filter.rs

## Purpose

This module defines a RocksDB compaction filter factory and filter for removing expired RawKV entries during compaction.

## Important APIs, Types, And Functions

`TtlCompactionFilterFactory<F: KvFormat>` implements RocksDB's `CompactionFilterFactory`. It inspects input table TTL properties and creates a `TtlCompactionFilter<F>` only when at least one input table may contain expired entries. `TtlCompactionFilter<F>` stores the current timestamp and accumulated expired count/size. Its `featured_filter` decides whether each key/value should be kept or removed. Drop updates Prometheus counters in batches.

## Control Flow

Factory creation reads `RocksTtlProperties` from input table user-collected properties and computes `min_expire_ts`. If all table min-expire timestamps are in the future, no filter is installed. Otherwise a filter named `ttl_compaction_filter` is returned. During compaction, the filter ignores non-value records, non-data keys, and non-raw key modes. It decodes raw values; expired values with `expire_ts <= self.ts` are removed and counted, decode errors are logged and counted as `ts_error`, and all other values are kept.

## State And Persistence Behavior

The filter removes expired entries from RocksDB output during compaction. Per-filter counters are local until `Drop`, then increment global `TTL_EXPIRE_KV_SIZE_COUNTER` and `TTL_EXPIRE_KV_COUNT_COUNTER`. It records `ts` once at filter creation, so a long compaction uses a stable expiration cutoff.

## Dependencies And Integration Points

It integrates RocksDB raw compaction filter traits, TiKV API version key/value decoding through `KvFormat`, `keys::DATA_PREFIX_KEY`, raw TTL timestamp helpers, Rocks TTL table properties, and TTL checker action metrics.

## Risks And Edge Cases

The factory skips filter creation based on table-level min expiration. Incorrect or absent TTL properties can delay cleanup. Decode errors keep the value to avoid data loss but emit error metrics and logs. Only raw-mode data keys are affected, so transactional or metadata keys are protected by key-mode checks.

## Test Signals

No local tests are present. Expected coverage comes from RocksDB compaction filter integration and RawKV TTL tests elsewhere.
