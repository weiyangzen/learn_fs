# sources/storage-engines/pebble/sstable/tablefilters/bloom/adaptive_policy.go

## Purpose
Adds an adaptive Bloom table filter policy that caps filter byte size by reducing bits per key when necessary.

## Important APIs, Types, And Functions
`AdaptivePolicy(targetBitsPerKey, maxFilterSize)` returns `adaptivePolicyImpl`. `adaptivePolicyImpl.Name` emits `adaptive_bloom(target,max)`, and `NewWriter` returns `adaptiveFilterWriter`. `adaptiveFilterWriter.AddKey` and `Finish` build the filter. `FilterSize` computes serialized size, and `MaxBitsPerKey` finds the largest bits/key fitting a byte limit.

## Control Flow
The writer collects hashes like a normal Bloom writer. On `Finish`, it computes the target filter size; if larger than `maxSize`, it calls `MaxBitsPerKey`. If the result is below 2 bits/key, it declines to build a filter. Otherwise it builds a standard cache-line Bloom filter with adjusted probes and line count.

## State And Persistence Behavior
The policy name and generated Bloom filter bytes persist in SSTables. Adaptive decisions are per-filter at finish time, based on collected key count and configured byte limit.

## Dependencies And Integration Points
Depends on Bloom `hashCollector`, `FilterSize`, `calculateNumLines`, `calculateProbes`, `buildFilter`, `Family`, Pebble filter interfaces, and invariants. Name parsing is integrated in `bloom.PolicyFromName`.

## Risks And Edge Cases
A too-small max size suppresses the filter entirely. The max-size math must honor odd cache-line counts and trailer bytes. Lowering bits/key trades memory for higher FPR; one-bit filters are intentionally rejected as not useful.

## Test Signals
`adaptive_policy_test.go` covers size math, policy behavior, randomized max sizes, and name parsing.
