# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/tasks/ContainerKeyMapperTaskOBS.java

Purpose: `ReconOmTask` wrapper that runs container-key mapping for Object Store bucket keys.

Important APIs: `getStagedTask`, `reprocess`, `process`, and `getTaskName`.

Control flow and persistence: reprocess loads the same parallelism and flush-threshold configs as the FSO task and delegates to `ContainerKeyMapperHelper.reprocess` with `BucketLayout.OBJECT_STORE`. Incremental processing filters the OM update batch to `keyTable` events.

Dependencies and integration: writes to the same Recon container-key tables and shared per-container count map as the FSO task. It is intended to run beside FSO so total container counts include both layouts.

Risks: hardcoded `keyTable` string can drift from OM constants. OBS and Legacy data can both be present in OM key table in other parts of Recon; this task uses `BucketLayout.OBJECT_STORE` for reprocess but incremental filtering is table-only and relies on upstream task assignment/event validity to avoid Legacy contamination.

Test signals: assert OBS reprocess only scans object-store key table, process handles only key-table events, and shared helper state is correct when paired with FSO.
