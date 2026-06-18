# sources/storage-engines/rocksdb/util/random.cc

## Purpose
Provides out-of-line implementations for RocksDB's lightweight deterministic random generator string helpers and per-thread random instance.

## Important APIs, Types, And Functions
`Random::GetTLSInstance` constructs a thread-local `Random` in aligned storage using the current thread id hash as seed. `Random::HumanReadableString`, `Random::RandomString`, and `Random::RandomBinaryString` fill strings with lowercase letters, printable ASCII, or binary-ish byte values respectively.

## Control Flow
`GetTLSInstance` checks a `thread_local` pointer and placement-news a `Random` into `thread_local` aligned storage on first use. String methods resize the return string and fill each byte using `Uniform`.

## State And Persistence
State is per-thread process memory: a `thread_local Random*` and backing aligned storage. It is not persisted and intentionally avoids locking. The placement-created `Random` has thread lifetime and no explicit destructor path.

## Dependencies And Integration Points
Depends on `util/random.h`, `port/likely.h`, `util/aligned_storage.h`, and thread id hashing. Used by tests and internal randomized operations needing cheap deterministic-ish randomness without cryptographic guarantees.

## Risks
The TLS seed is derived from `std::hash<std::thread::id>()`, so it is not reproducible across implementations and not secure. `RandomBinaryString` uses `Uniform(CHAR_MAX)`, which excludes `CHAR_MAX` and is not full-byte entropy if `char` has 8 bits. String methods inherit modulo bias from `Random::Uniform`.

## Test Signals
`random_test.cc` covers distribution properties for `Uniform`, `OneIn`, `OneInOpt`, and `PercentTrue`, indirectly validating the generator used by these helpers but not the string helpers or TLS initialization.
