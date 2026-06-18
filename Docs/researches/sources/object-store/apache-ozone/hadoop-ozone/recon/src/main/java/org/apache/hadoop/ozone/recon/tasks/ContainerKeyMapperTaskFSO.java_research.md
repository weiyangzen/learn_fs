# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskFSO.java

Purpose: `ReconOmTask` wrapper that runs container-key mapping for File System Optimized buckets.

Important APIs: constructor injection of `ReconContainerMetadataManager` and `OzoneConfiguration`, `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess reads tuning knobs for flush threshold, max keys in memory, iterators, and workers, then delegates to `ContainerKeyMapperHelper.reprocess` with `BucketLayout.FILE_SYSTEM_OPTIMIZED`. Incremental process delegates to the helper for the `fileTable` event stream.

Dependencies and integration: participates with `ContainerKeyMapperTaskOBS` through helper static coordination. Staged tasks use the staged Recon DB store so full snapshot rebuilds can be swapped atomically.

Risks: the helper's static active-task coordination assumes FSO and OBS reprocess lifecycles align. Table name is hardcoded as `fileTable`, while other code sometimes imports constants, so OM table-name changes would break filtering silently.

Test signals: verify `getTaskName`, staged manager wiring, config propagation, file-table filtering, and concurrent FSO/OBS rebuild behavior.
