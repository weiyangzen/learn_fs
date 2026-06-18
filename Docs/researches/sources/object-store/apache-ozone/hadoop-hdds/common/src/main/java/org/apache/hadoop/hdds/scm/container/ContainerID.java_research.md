# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/scm/container/ContainerID.java

## Purpose
Immutable typed wrapper around a numeric container ID. It prevents accidental mixing of container IDs with unrelated longs and provides codecs/protobuf conversion.

## Important APIs, Types, And Functions
`valueOf(long)`, `getBytes(long)`, `getProtobuf()`, `getFromProtobuf`, `getCodec()`, `compareTo`, `equals`, `hashCode`, and `toString` are the key APIs. The class memoizes protobuf and hash values with Ratis `MemoizedSupplier`.

## Control Flow
Factory construction validates non-negative IDs. Consumers serialize through `LongCodec`/`DelegatedCodec` or `HddsProtos.ContainerID`.

## State And Persistence
Instances hold a final `long id`. The codec persists IDs as longs in SCM metadata DBs. `MIN` is `0`.

## Dependencies And Integration Points
Depends on Guava preconditions, HDDS DB codecs, HddsProtos, and JCIP immutability annotation. Used throughout container manager, replication, exclude lists, and reports.

## Risks And Test Signals
The deprecated `getId()` still exposes raw longs for compatibility. Tests should cover negative rejection, codec/protobuf round trip, ordering, memoized hash consistency, and map/set behavior.
