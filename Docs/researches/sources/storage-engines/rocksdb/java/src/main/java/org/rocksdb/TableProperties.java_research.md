# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/TableProperties.java

## Purpose
`TableProperties` is the Java immutable snapshot of read-only SST/table properties exposed by RocksDB.

## Important APIs and Types
The package-private constructor accepts native-supplied values for data/index/filter sizes, key/value raw sizes, block and entry counts, delete/merge/range-delete counts, format metadata, column-family identity, creation/oldest-key times, compression estimates, external SST global sequence offset, policy/comparator/operator names, user-collected properties, and readable properties. Getters expose each field. Equality and hash code compare all fields, including `columnFamilyName` with `Arrays.equals`.

## Control Flow
The class performs no computation beyond storing constructor values and returning them. Equality performs a field-by-field comparison; hash code combines object fields and the byte-array hash.

## State and Persistence Behavior
It is a Java snapshot of persistent table metadata but does not persist or mutate anything. `columnFamilyName`, `userCollectedProperties`, and `readableProperties` are stored and returned directly, so caller mutation can alter the apparent value object.

## Dependencies and Integration Points
It is returned by `SstFileReader.getTableProperties`, table properties APIs, event DTOs, and table filters. It references `IndexType#kTwoLevelIndexSearch` in documentation.

## Risks and Test Signals
Tests should validate JNI constructor field ordering, null optional strings, map conversion, equality/hash behavior, compression estimate fields, external SST global seqno offset, and direct-return mutability. A risk is value-object aliasing through arrays/maps; another is that new native table properties require constructor and equality updates.
