# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/MetaStoreIterator.java

## Purpose
`MetaStoreIterator<T>` is a minimal iterator extension for metadata-store backends. It adds bidirectional positioning primitives to Java `Iterator<T>` so callers can seek to the first or last entry.

## Important APIs and Types
The interface extends `Iterator<T>` and declares `seekToFirst()` and `seekToLast()`. It does not define close semantics, prefix seeking, or typed key/value access.

## Control Flow and State
The interface itself has no control flow or state. Implementations are expected to maintain backend cursor state and move that cursor to the first or last record when requested.

## Persistence, Dependencies, and Integration
The only direct dependency is `java.util.Iterator`. It acts as a common contract for metadata database iterators, including RocksDB-backed table iterators elsewhere in the HDDS utility DB package.

## Risks and Test Signals
Because this interface does not extend `Closeable`, resource-owning implementations need their own cleanup contract or wrapper. Tests should verify implementation-specific cursor movement, empty-store behavior, `next`/`hasNext` semantics after seeking, and how `seekToLast` behaves for prefix-limited iterators.
