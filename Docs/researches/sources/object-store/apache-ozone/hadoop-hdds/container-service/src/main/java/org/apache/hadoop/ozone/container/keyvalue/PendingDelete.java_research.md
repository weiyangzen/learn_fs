# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/PendingDelete.java

## Purpose
`PendingDelete` is an immutable value object holding pending deletion block count and pending deletion bytes for key-value container metadata and inspection output.

## Important APIs, Types, And Functions
It defines JSON field names `pendingDeleteBlocks` and `pendingDeleteBytes`, constructor `PendingDelete(long count, long bytes)`, package-private `addToJson(ObjectNode)`, and getters `getCount`/`getBytes`.

## Control Flow
Startup/inspection code constructs it from metadata-table values or recalculated delete transaction aggregates. `addToJson` serializes the two values into a Jackson object with stable field names.

## State And Persistence
The object is in-memory only. It reflects persisted RocksDB metadata or derived delete-transaction data but does not persist anything itself.

## Dependencies And Integration Points
It depends on Jackson `ObjectNode` and is consumed by `KeyValueContainerUtil` and metadata inspector paths when setting container pending-deletion statistics.

## Risks And Test Signals
Risk is mostly field-name drift or count/byte interpretation across layout features. Test signals include JSON output, zero-byte legacy cases, and startup metadata population from stored and recalculated values.
