# sources/sync-backup/syncthing/lib/rand/random.go

## Purpose
Provides convenience functions similar to `math/rand`, but backed by a concurrency-safe cryptographic random source.

## Important APIs, Types, and Functions
Exports `Reader`, `Read`, `String`, `Int63`, `Uint64`, `Intn`, and `Shuffle`. `randomCharset` defines the alphabet for random strings, excluding ambiguous characters. `defaultSecureSource` and `defaultSecureRand` provide package-level secure randomness.

## Control Flow
`Read` fills a byte slice from `defaultSecureSource`. `String` builds a string of requested length by repeatedly selecting random indexes from `randomCharset` via `defaultSecureRand.Intn`. `Int63` and `Uint64` delegate to the secure source. `Shuffle` uses reflection to get length and a swapper, returns early for length less than two, and delegates to `math/rand.Rand.Shuffle` backed by secure entropy.

## State and Persistence Behavior
Package-level random source and rand instance hold buffered entropy state in memory. There is no persistence. The secure source serializes access internally; however, `math/rand.Rand` itself has mutable state, so package-level methods depend on the secure source locking for entropy reads.

## Dependencies and Integration Points
Depends on `io`, `math/rand`, `reflect`, `strings`, and `securesource.go`. Used by relay address shuffling and general Syncthing code needing secure random IDs or tokens.

## Risks and Edge Cases
`Intn` panics for `n <= 0` as `math/rand` does. `Shuffle` will panic if given a non-slice or non-swappable value through `reflect.Swapper`. Random string tests detect duplicates statistically, so extremely unlikely false failures are theoretically possible. The alphabet provides about 5.8 bits per character, so callers must choose adequate length for secrets.

## Test Signals
`random_test.go` verifies requested string lengths, no duplicates across 1,000 eight-character strings, no duplicate uint64s across 1,000 values, and benchmarks string allocation/performance.
