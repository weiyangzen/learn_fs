# sources/storage-engines/foundationdb/bindings/java/src/main/com/apple/foundationdb/LocalityUtil.java

## Purpose
`LocalityUtil` exposes advanced locality helpers for discovering key-server boundary keys and storage server addresses for a key.

## Important APIs, Types, And Functions
`getBoundaryKeys(Database, byte[], byte[])` and `getBoundaryKeys(Transaction, byte[], byte[])` return `CloseableAsyncIterator<byte[]>`. `getAddressesForKey(Transaction, byte[])` delegates to `FDBTransaction`. `BoundaryIterator` implements retrying iteration over system keyspace. `keyServersForKey` prefixes keys with `\xff/keyServers/`.

## Control Flow
Boundary iteration creates or derives a transaction, enables system-key and lock-aware options, scans `/keyServers/` system keys, strips the prefix from each returned key, advances `begin`, and composes `onHasNext` with retry handling. On transaction-too-old after progress, it creates a fresh transaction and restarts from the current boundary; other runtime errors flow through `onError`.

## State And Persistence Behavior
`BoundaryIterator` owns a transaction, current begin key, last begin, end key, current block iterator, next future, and closed flag. It must be closed to release the transaction; finalization warns and closes as a fallback.

## Dependencies And Integration Points
It depends on `Transaction`, `Database`, `AsyncIterator`, `CloseableAsyncIterator`, `AsyncUtil`, `ByteArrayUtil`, and transaction system-key options.

## Risks And Edge Cases
Boundary results are approximate and non-transactional. `next` requires a completed positive `onHasNext`; otherwise it throws. Only real `FDBTransaction` supports address lookup; wrappers get locality-unavailable errors.

## Test Signals
Tests should cover prefix construction, boundary iteration over multiple blocks, retry after transaction-too-old, close/finalizer behavior, unsupported transaction address lookup, and options set on locality transactions.
