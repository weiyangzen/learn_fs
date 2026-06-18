# sources/storage-engines/tikv/components/in_memory_engine/src/lib.rs

## Purpose

Crate root for TiKV's in-memory engine component. It declares internal modules, exposes the public API surface used by TiKV integration code and tests, and defines `InMemoryEngineContext`, the construction bundle for config, statistics, and PD access.

## Important APIs, Types, And Functions

The crate enables nightly features `core_intrinsics`, `slice_pattern`, and `str_as_str`, then declares modules for background work, config, cross-checking, engine, keys, memory control, metrics, performance context, reads, region labels/managers/stats, statistics, tests, and write batches. Re-exports include `BackgroundRunner`, `BackgroundTask`, `GcTask`, `InMemoryEngineConfig`, `RegionCacheMemoryEngine`, `SkiplistHandle`, key helpers/types, `flush_in_memory_engine_statistics`, `RegionCacheSnapshot`, `RegionCacheStatus`, `RegionState`, `Statistics as InMemoryEngineStatistics`, and `RegionCacheWriteBatch`.

`InMemoryEngineContext` stores `Arc<VersionTrack<InMemoryEngineConfig>>`, `Arc<InMemoryEngineStatistics>`, and `Arc<dyn PdClient>`. `new` accepts real config and PD client. `new_for_tests` installs a mock PD client whose `get_tso` returns a composed physical-now timestamp. Accessors expose cloned PD/statistics handles and a config reference.

## Control Flow

Consumers create `InMemoryEngineContext`, pass it into `RegionCacheMemoryEngine::new` or `with_region_info_provider`, and the engine extracts config/statistics/PD client during construction. Test code can avoid external PD setup through `new_for_tests`.

## State And Persistence Behavior

The crate root holds no storage state beyond the context wrapper. `InMemoryEngineContext` is cloned by value and shares all underlying state through `Arc`s. Statistics are initialized with `Arc::default()` and then shared with engine/metrics flushing.

## Dependencies And Integration Points

Uses `pd_client::PdClient`, `tikv_util::config::VersionTrack`, `txn_types::TimeStamp`, and `futures::future::ready` for the test PD client. It is the public entry point tying together the local modules reviewed in this subset and the rest of TiKV.

## Risks

The public re-export list defines what downstream code can rely on; changing it can break integration tests or TiKV call sites. `new_for_tests` only implements `get_tso`, so tests that require other PD methods must use a richer mock. Nightly feature gates tie this crate to a compiler/runtime environment that supports those internal features.

## Test Signals

No direct tests are in `lib.rs`, but every module test using `InMemoryEngineContext::new_for_tests`, `RegionCacheMemoryEngine`, re-exported key helpers, snapshots, and write batches exercises this public API surface.
