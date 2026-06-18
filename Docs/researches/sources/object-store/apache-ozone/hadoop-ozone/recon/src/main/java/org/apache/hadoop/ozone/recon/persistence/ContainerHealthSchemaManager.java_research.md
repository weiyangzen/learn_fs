## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/persistence/ContainerHealthSchemaManager.java

Purpose: SQL/jOOQ manager for the `UNHEALTHY_CONTAINERS` table used by container health scanning and APIs.

Important APIs/types/functions: `insertUnhealthyContainerRecords`; `batchDeleteSCMStatesForContainers`; `replaceUnhealthyContainerRecordsAtomically`; `getExistingInStateSinceByContainerIds`; `applyExistingInStateSince`; `getUnhealthyContainersSummary`; `getUnhealthyContainers`; `getUnhealthyContainersCount`; `getUnhealthyContainersCursor`; nested `UnhealthyContainerRecord`, `ContainerStateKey`, and `UnhealthyContainersSummary`.

Control flow: inserts are batched in chunks of 1000. Deletes and existing-state lookups chunk container IDs by `MAX_IN_CLAUSE_CHUNK_SIZE` to avoid Derby generated-bytecode limits. Atomic replace runs delete and insert in one jOOQ transaction. Query methods support forward/reverse pagination, count capping, and lazy cursor streaming with configured fetch size.

State and persistence: owns all SQL operations for unhealthy container records and preserves `inStateSince` for unchanged `(containerId,state)` pairs. Depends on `ContainerSchemaDefinition`, jOOQ generated table classes, `OzoneConfiguration`, and Recon server fetch-size config.

Risks: `applyExistingInStateSince` performs its own lookup, so callers that already fetched existing values may duplicate DB work. Cursor callers must close returned cursors. Count method requires non-null state. Tests should cover Derby chunking, atomic rollback, state preservation, each allowed state deletion, pagination direction, cursor fetch size, capped counts, summaries, and DB exception fallbacks.
