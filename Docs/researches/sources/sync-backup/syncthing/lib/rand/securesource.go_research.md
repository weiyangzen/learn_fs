# sources/sync-backup/syncthing/lib/rand/securesource.go

## Purpose
Implements a concurrency-safe `math/rand.Source64`-style secure entropy source backed by `crypto/rand.Reader`, with buffering for performance.

## Important APIs, Types, and Functions
`secureSource` contains a buffered reader, mutex, and reusable 8-byte buffer. `newSecureSource` wraps `crypto/rand.Reader` in `bufio.Reader`. Methods are `Seed`, `Int63`, `Read`, and `Uint64`.

## Control Flow
`Seed` panics because the source must not be deterministic. `Read` locks and delegates to the buffered reader. `Uint64` locks, reads exactly eight bytes into the reusable buffer, panics on entropy failure, and decodes little-endian. `Int63` masks off the top bit of `Uint64`.

## State and Persistence Behavior
State is in-memory buffering around the OS random source plus a mutex and scratch buffer. No generated values are persisted. The lock protects both buffered reader state and the scratch buffer.

## Dependencies and Integration Points
Depends on `bufio`, `crypto/rand`, `encoding/binary`, `io`, and `sync`. It backs `random.go` package-level functions and can be used as an `io.Reader`.

## Risks and Edge Cases
An OS entropy read failure panics in `Uint64`, which is appropriate for security-sensitive randomness but can crash callers. `Read` may return a short read if the underlying reader does; package-level `Read` wraps it with `io.ReadFull`. Buffering improves performance but requires correct locking.

## Test Signals
`securesource_test.go` samples two independent sources, checks for duplicate values, verifies the top bit is never set for `Int63`, checks rough bit distribution, and benchmarks `Int63`.
