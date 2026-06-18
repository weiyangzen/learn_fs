# sources/storage-engines/tikv/components/causal_ts/src/tso.rs

## Purpose
Implements a PD-backed causal timestamp provider that caches ranges of TSOs, renews them adaptively, and tolerates short PD failures by allocating ahead.

## APIs, Types, And Functions
`TsoBatch` represents one logical timestamp range for a physical time. `TsoBatchList` is an ordered, lock-protected collection with `pop`, `push`, `flush`, `remain`, `usage`, and `take_and_report_usage`. `BatchTsoProvider<C: PdClient>` owns the PD client, shared batch list, TiKV worker, renewal parameters, interval, and renewal request channel. Public constructors are `new` and `new_opt`; provider methods implement `CausalTsProvider`. `SimpleTsoProvider` is a request-per-call test implementation.

## Control Flow
Initialization spawns a renew worker, performs an initial flush renew, and optionally schedules periodic background renew. `async_get_ts` first pops from cache; if empty, it renews up to three times for `used_up` before returning `TsoBatchUsedUp`. `async_flush` renews with `need_flush`, then returns the first new timestamp. Renew requests are coalesced in `renew_thread`; if any request needs flush, the single PD batch renew flushes old cached TSOs before inserting the new range.

## State And Persistence
State is in memory: ordered timestamp batches, approximate remain/usage counters, atomic allocation offsets, renewal request channel, worker tasks, and metrics. There is no durable timestamp persistence in this file; monotonicity depends on PD-provided TSOs and local rejection of fallback ranges.

## Dependencies And Integration Points
Depends on `pd_client::PdClient::batch_get_tso`, TiKV workers, tokio channels/oneshots, parking_lot `RwLock`, metrics, and `txn_types::TimeStamp`. Higher-level components use the `CausalTsProvider` trait.

## Risks And Test Signals
Critical risks are timestamp fallback, losing causality on flush, stale batches under concurrent readers, counter imprecision, PD renew failure behavior, and large allocation pressure. `RwLock<BTreeMap>` is intentionally chosen so flush synchronization prevents readers from acquiring removed batches. Tests cover batch boundaries, adaptive batch sizing, fallback rejection, capacity eviction, pop-after-ts, simple provider, provider renew/flush/used-up behavior, and failure recovery.
