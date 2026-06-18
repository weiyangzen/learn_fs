# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/OpenKeysInsightHandler.java

Purpose: `OpenKeysInsightHandler` implements `OmTableHandler` for open key and open file tables. It maintains counts and size totals for unclosed keys visible in Recon insights.

Important APIs and types: `handlePutEvent` casts the event value to `OmKeyInfo`, increments count, logical size, and replicated size. `handleDeleteEvent` subtracts those values with zero floors. `handleUpdateEvent` requires both old and new `OmKeyInfo` and applies size deltas without changing count. `getTableSizeAndCount` scans the OM table and totals `OmKeyInfo.getDataSize()` and `getReplicatedSize()`.

Control flow and integration: `OmTableInsightTask` registers this handler for `OPEN_KEY_TABLE` and `OPEN_FILE_TABLE`. Incremental deltas mutate maps that are later persisted to global stats. Full reprocess iterates the actual OM table.

State and persistence: the handler is stateless. Durable state is the caller's eventual write to Recon global stats.

Dependencies: HDDS `Table` and `TableIterator`, `OMMetadataManager`, `OmKeyInfo`, Commons `Triple`.

Risks and test signals: casts assume validated event payload type. Delete subtraction uses `size > delta ? size - delta : 0`, so exact equality becomes zero as intended. Update can drive values negative if old value exceeds current map value. Tests should cover put/delete/update, missing old values, null values, iterator close behavior, and both open key and open file table names.
