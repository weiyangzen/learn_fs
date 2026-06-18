# sources/test-tools/fio/filehash.h

## Purpose
`filehash.h` declares the global fio file hash and bloom filter interface.

## Important APIs, Types, And Functions
The header exposes initialization/exit, filename lookup, add/remove, explicit hash lock/unlock, and `file_bloom_exists(const char *, bool)`. It forward-depends on `struct fio_file` being visible to consumers that use pointer-returning APIs and includes `lib/types.h` for `bool`.

## Control Flow
The header has no logic. Consumers initialize the subsystem, then use lookup/add/remove under internal locking or wrap batches with explicit lock helpers.

## State And Persistence
State is owned by `filehash.c`, not the header. Bloom state is process lifetime and approximate.

## Dependencies And Integration Points
This header is included by file setup code and any component that needs filename deduplication. It integrates with `fio_file` hash flags and list linkage.

## Risks
The API does not document ownership or whether callers may call functions before init/after exit. Explicit lock helpers expose internal synchronization and can deadlock if callers mix them incorrectly with functions that also lock.

## Test Signals
Compile tests should include this header from C and C++ contexts where `struct fio_file` is forward-declared. Behavioral tests belong to `filehash.c`.
