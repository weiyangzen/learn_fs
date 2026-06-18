# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperHelper.java

Purpose: Shared implementation for FSO and OBS container-key mapper tasks. It builds and maintains mappings from containers to key prefixes, reverse mappings from key prefixes to containers, and per-container key counts.

Important APIs: static `reprocess`, `process`, `handleKeyReprocess`, `flushAndCommitContainerKeyInfoToDB`, and test-only `clearSharedContainerCountMap`. Private handlers translate OM PUT, DELETE, and UPDATE events into container-key map changes.

Control flow and persistence: reprocess uses `ParallelTableIteratorOperation` over one bucket layout, worker-local `ContainerKeyPrefix` maps, and a static cross-task `ConcurrentHashMap<Long, AtomicLong>` for container counts. Static initialization truncates shared tables once across FSO and OBS. The last active task writes the shared count map, increments total container count, clears shared state, and resets the initialization flag. Incremental process filters by table, builds local add/delete/count deltas, scans reverse index for deletes, and commits a single batch.

Dependencies and integration: called by `ContainerKeyMapperTaskFSO` and `ContainerKeyMapperTaskOBS`; writes through `ReconContainerMetadataManager`; reads OM key location versions and container IDs.

Risks: correctness depends on both reprocess tasks participating; if only one task runs, the active counter and global state semantics can surprise. Exceptions before decrement can leave the static active count or initialization flag stale. Incremental container count updates use SQL read-modify-write. Delete handling scans reverse index and local map, so key equality/version semantics are important.

Test signals: cover concurrent FSO/OBS reprocess, failure cleanup, duplicate key versions, delete after put in same batch, update with missing old value, and shared-state reset between tests.
