# sources/storage-engines/pebble/internal/testkeys/testkeys.go

## Purpose
This package provides deterministic, human-readable key generation and comparison utilities for Pebble tests and benchmarks. It models keys with optional MVCC-like timestamp suffixes (`@<integer>`) and offers finite keyspaces, slicing, striding, random prefix generation, and test KV metadata extraction.

## Important APIs, Types, and Functions
`Comparer` is a Pebble `base.Comparer` that compares unsuffixed prefixes lexicographically and timestamp suffixes in descending numeric order; it also supplies separator, successor, immediate successor, split, validation, and suffix comparison hooks. `Keyspace` abstracts finite key generators with `Count`, `MaxLen`, and `key`. Public helpers include `Alpha`, `Divvy`, `Slice`, `EveryN`, `Key`, `KeyAt`, `WriteKey`, `WriteKeyAt`, `Suffix`, `SuffixLen`, `ParseSuffix`, `WriteSuffix`, `RandomPrefixInRange`, and `ExtractKVMeta`. Internal helpers implement alphabet key enumeration and inverse indexing.

## Control Flow and State
The comparer splits keys at the last `@`. Prefixes compare bytewise; suffixes parse numeric timestamps and reverse the ordering so larger timestamps sort earlier. Point suffix comparison ignores the `_synthetic` suffix while range suffix comparison uses it as a tiebreaker. Alphabet keyspaces enumerate variable-length strings from `a` to `z` in a deterministic tree order. `RandomPrefixInRange` validates bounds, trims common prefixes, maps bounds into an alphabet index range, and samples a prefix with assertions that the result lies in `[a,b)`. State is mostly immutable; the package-level inverse alphabet map is populated in `init`.

## Dependencies and Integration
The package depends on `base`, `math/rand/v2`, `regexp`, `strconv`, `strings`, and Cockroach errors. It is widely integrated into Pebble internal tests, datadriven fixtures, range-key tests, and manifest parsing tests as a consistent comparer and key generator.

## Risks and Edge Cases
`keyCount` panics on overflow, and comments note `RandomPrefixInRange` uses max lengths below the overflow region. `ImmediateSuccessor` panics if called with a suffixed key. Invalid suffixes panic in compare paths, so tests must validate keys when needed. `Slice` rejects `i >= Count`, which means an empty slice at the end is not allowed. `_synthetic` suffix handling deliberately differs between point and range suffix comparison, so changes can violate comparer contracts.

## Test Signals
`testkeys_test.go` covers key generation, inverse indexing, counts, full keyspaces, slicing, suffix ordering, suffix length, divvying, random prefix generation including randomized insertion, overflow panic, comparer checks, synthetic suffix behavior, and tiering metadata extraction.
