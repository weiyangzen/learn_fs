# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/FDBTransaction.java

## Purpose
`FDBTransaction` is the concrete native-backed implementation of `Transaction`. It exposes reads, writes, conflict ranges, range queries, mapped range queries, commit, retry/reset semantics, watches, locality address lookup, and snapshot reads.

## Important APIs, Types, And Functions
The class extends `NativeObjectWrapper` and implements `Transaction` and `OptionConsumer`. It owns `database`, `executor`, `TransactionOptions`, optional `EventKeeper`, a `transactionOwner` flag, and a `ReadSnapshot` view. Public methods wrap native transaction calls for read versions, `get`, `getKey`, range reads, mapped range reads, conflict ranges, mutations, commit, committed version, versionstamp, approximate size, watch, `onError`, cancel, and key locations.

## Control Flow
Most methods increment instrumentation, acquire `pointerReadLock`, call JNI using `getPtr`, wrap native futures in typed `NativeFuture` subclasses, and release the lock. Snapshot methods route reads through the same transaction with the snapshot flag and suppress read conflict additions. Range methods construct lazy `RangeQuery` or `MappedRangeQuery` objects. `onError` unwraps completion exceptions, rejects non-`FDBException`s, calls native `Transaction_onError`, transfers pointer ownership to a new transaction wrapper, invalidates the old wrapper, and closes the replacement on retry failure.

## State And Persistence Behavior
The native pointer is single-owner except during `onError` transfer. After transfer, the old transaction throws on further pointer access. Write mutations and conflict ranges are stored by the native transaction until commit/reset/dispose. No Java-side persistence occurs; close disposes the native transaction if still owner.

## Dependencies And Integration Points
It integrates with `Database`, `ReadTransaction`, `Transaction`, `RangeQuery`, `MappedRangeQuery`, all typed future classes, `ByteArrayUtil`, `StreamingMode`, `MutationType`, `ConflictRangeType`, `TransactionOptions`, and native JNI transaction functions.

## Risks And Edge Cases
Using a transaction after `onError` invalidates it. Null validation exists for `set` and `clear`, but not every native call validates all byte arrays before JNI. Snapshot mapped ranges are unsupported. Range iterators must not outlive the transaction for long. The unused native `Transaction_reset` declaration suggests historical API drift.

## Test Signals
Tests should cover point reads, snapshot reads, key selectors, range and mapped range iteration, conflict range behavior, mutation null checks, commit and committed version, `onError` pointer invalidation, cancel/watch, close idempotence, instrumentation counts, and transaction-use-after-reset errors.
