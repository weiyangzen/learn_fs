# sources/storage-engines/foundationdb/fdbserver/workloads/SelectorCorrectness.cpp

## Purpose
`SelectorCorrectnessWorkload` stress-tests key selectors and range reads over a synthetic numeric keyspace. It validates direct `get` expectations and selector-bounded `getRange` result sizes, both with and without read-your-writes mutations.

## Important APIs, Types, And Functions
It derives from `TestWorkload` and registers as `SelectorCorrectness`. Important members are operation count bounds, `maxKeySpace`, `maxOffset`, `testReadYourWrites`, `transactions`, and `retries`. Core actors are `SelectorCorrectnessSetup` and `SelectorCorrectnessClient`.

## Control Flow
Setup writes even-numbered keys. In RYW mode it writes keys divisible by four and randomly writes keys congruent to two. The client repeatedly creates a native `Transaction` and a `ReadYourWritesTransaction`; in RYW mode it stages additional writes before reads. Each loop randomly performs either point get validation or selector range validation with randomized `onEqual`, offset, and reverse flags. It computes expected result size algebraically and compares actual range size below `maxKey`.

## State And Persistence Behavior
Setup persists the base key distribution. RYW-mode per-transaction writes are local to the `ReadYourWritesTransaction` and are not committed by the client loop. Native mode validates persisted even keys only. Transactions are reset after each operation batch.

## Dependencies And Integration Points
It uses NativeAPI transactions, `ReadYourWritesTransaction`, key selector APIs, tester workload metrics, and deterministic random key generation. It is an API semantics workload rather than a storage durability test.

## Risks And Edge Cases
The constructor appears to read `maxOperationsPerTransaction` from the `minOperationsPerTransaction` option key, which may unintentionally ignore a distinct max option. Error handling calls `trRYOW.onError(err)` even when native `tr` was used, so retry semantics are mostly relevant to the RYW transaction object. Expected-size arithmetic is compact and sensitive to selector boundary conventions.

## Test Signals
Failures emit `RanSelTestFailure` with reasons for missing/present values or range size mismatches. Metrics report transactions and retries. `check` clears clients and returns true, so severe trace events are the primary failure signal.
