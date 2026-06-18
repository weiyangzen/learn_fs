# sources/storage-engines/tikv/components/causal_ts/benches/tso.rs

## Purpose
Criterion benchmarks for the cached TSO list and PD-backed batch provider.

## APIs, Types, And Functions
Benchmarks include `bench_batch_tso_list_pop`, `bench_batch_tso_list_push`, `bench_batch_tso_provider_get_ts`, and `bench_batch_tso_provider_flush`. They use `TsoBatchList`, `BatchTsoProvider`, `CausalTsProvider`, `TestPdClient`, and `TimeStamp`.

## Control Flow
List pop benchmarks prefill batches, then repeatedly pop. Push benchmarks repeatedly insert batches. Provider benchmarks construct a provider with background renewal disabled by `Duration::ZERO`, then call `async_get_ts` or `async_flush` through `block_on`.

## State And Persistence
All state is in-memory benchmark state, including fake PD client TSO and cached batch lists.

## Dependencies And Integration Points
Exercises both the low-level cache and the high-level provider API. Uses the same test PD client as unit tests to avoid real PD dependency.

## Risks And Test Signals
Useful for detecting lock/contention overhead in `TsoBatchList` and async-channel overhead in provider renew/flush paths. It does not validate correctness beyond successful execution.
