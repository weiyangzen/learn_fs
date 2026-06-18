# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/DeletedKeysInsightHandler.java

Purpose: `OmTableHandler` for OM's deleted key table. It maintains object counts and replicated/unreplicated sizes for keys pending backend deletion.

Important APIs: `handlePutEvent`, `handleDeleteEvent`, no-op `handleUpdateEvent`, and `getTableSizeAndCount`.

Control flow and persistence: incremental PUT casts the event value to `RepeatedOmKeyInfo`, adds the number of contained key infos, and adds total sizes. DELETE subtracts those values with floor-at-zero guards. Reprocess iterates `omMetadataManager.getDeletedTable()` and aggregates totals from all `RepeatedOmKeyInfo` rows.

Dependencies and integration: used by broader OM table insight tasks through the `OmTableHandler` interface. It depends on `RepeatedOmKeyInfo.getTotalSize`, table-derived metric keys from the interface, and Recon global stats maps supplied by the caller.

Risks: PUT/DELETE casts are unchecked. Reprocess assigns `unReplicatedSize += result.getRight()` and `replicatedSize += result.getLeft()`, while incremental PUT uses left for unreplicated and right for replicated; this apparent swap is a high-value correctness check. Update is no-op because deleted-key sizes are assumed immutable.

Test signals: existing `TestOmTableInsightTask` references deleted table handling. Tests should verify left/right size semantics, multi-key repeated entries, null values, and floor-at-zero delete behavior.
