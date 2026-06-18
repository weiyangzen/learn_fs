# sources/storage-engines/foundationdb/fdbserver/kvstore/RocksDBCommon.h

## Purpose
This header declares shared RocksDB utility functions for FoundationDB kvstore code. It is a narrow interface that avoids exposing implementation details while giving storage engines consistent conversion and option-decoding behavior.

## Important APIs, Types, And Functions
Inside namespace `RocksDBCommon`, the header declares `toSlice(StringRef)`, `toStringRef(rocksdb::Slice)`, `getErrorReason(rocksdb::BackgroundErrorReason)`, `getWalRecoveryMode()`, `getWalRecoveryModeFromKnob(int)`, `getCompactionPriorityFromKnob(int)`, and `getIndexTypeFromKnob(int)`.

## Control Flow
The header contains no executable control flow beyond include guards and `WITH_ROCKSDB` conditional compilation. All behavior is implemented in `RocksDBCommon.cpp`.

## State And Persistence Behavior
The header declares stateless helpers. Its conversion functions are documented as conversions but callers must understand that the implementation returns non-owning view objects rather than durable copies.

## Dependencies And Integration Points
The declarations are available only when `WITH_ROCKSDB` is set. The header includes `fdbclient/FDBTypes.h` for `StringRef` and RocksDB `listener`, `options`, `slice`, and `table` headers for enum and type declarations. It is included by `KeyValueStoreShardedRocksDB.actor.cpp` and is suitable for other RocksDB kvstore implementations.

## Risks
Because the whole namespace is hidden behind `WITH_ROCKSDB`, callers must guard usage consistently or compilation fails in non-RocksDB builds. The header does not state ownership/lifetime caveats strongly enough for `toSlice` and `toStringRef`; misuse can produce dangling references.

## Test Signals
Header-level signals are compile coverage in both `WITH_ROCKSDB` and non-RocksDB builds, plus implementation tests for all declared functions. API users should include this header without relying on transitive RocksDB includes elsewhere.
