# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/db/RDBStoreByteArrayIterator.java

## Purpose
`RDBStoreByteArrayIterator` is the byte-array concrete implementation of `RDBStoreAbstractIterator`. It adapts RocksDB raw byte keys and values into `Table.KeyValue<byte[], byte[]>` records.

## Important APIs and Types
The constructor copies a non-empty prefix, stores the table/iterator/type through the superclass, and immediately seeks to the first matching entry. Implementations provide `key`, `getKeyValue`, `seek0`, `delete`, and `startsWithPrefix`.

## Control Flow and State
`getKeyValue` reads key and/or value depending on `IteratorType` flags, allowing key-only or value-only iteration. `startsWithPrefix` compares prefix bytes manually and treats null prefix as unrestricted.

## Persistence, Dependencies, and Integration
It reads from and can delete entries in a RocksDB-backed `RDBTable`. It depends on `ManagedRocksIterator`, `IteratorType`, and table key/value helpers.

## Risks and Test Signals
RocksDB byte arrays are exposed directly for current iterator values; callers should not assume long-lived defensive copies unless Rocks iterator semantics guarantee them. Tests should cover prefix copying isolation, empty prefix treated as no prefix, key/value read flags, seek behavior, delete behavior, short key mismatch, null key handling in prefix checks, and close through the superclass.
