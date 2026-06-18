# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreAbstractIterator.java

## Purpose
`RDBStoreAbstractIterator<RAW>` is the shared base for raw RocksDB table iterators. It implements `Table.KeyValueIterator<RAW, RAW>` over a managed Rocks iterator, with optional prefix restriction and delete-current-entry support.

## Important APIs and Types
Subclasses provide `key`, `getKeyValue`, `seek0`, `delete`, and `startsWithPrefix`. Implemented methods include `hasNext`, `next`, `seekToFirst`, `seekToLast`, `seek`, `removeFromDB`, `forEachRemaining`, and `close`.

## Control Flow and State
The iterator stores the managed Rocks iterator, optional table reference, optional prefix, iterator type, current entry, and an atomic close flag. `hasNext` returns false if the table DB is closed or Rocks iterator is invalid or prefix no longer matches. `next` captures current key/value, advances the Rocks iterator, and returns the captured entry. Prefix-limited `seekToFirst` seeks to the prefix; prefix-limited `seekToLast` is unsupported.

## Persistence, Dependencies, and Integration
Iteration reads persistent RocksDB data. `removeFromDB` mutates the table by deleting the current entry key. Dependencies include `ManagedRocksIterator`, `RDBTable`, table iterator contracts, and RocksDB exceptions.

## Risks and Test Signals
Callers must close iterators to maintain accurate resource/refcounting. `removeFromDB` depends on `currentEntry`, which is set by `next`/seek methods, not merely `hasNext`. Tests should cover empty iteration, prefix boundaries, DB-closed behavior, seek/seekToFirst/seekToLast, remove before/after next, double close idempotency, and iterator type key/value read flags.
