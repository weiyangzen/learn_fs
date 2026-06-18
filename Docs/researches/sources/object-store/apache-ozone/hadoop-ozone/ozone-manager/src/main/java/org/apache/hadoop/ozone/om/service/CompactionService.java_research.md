<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java

Purpose: Background service that periodically compacts configured OM RocksDB tables.

Important APIs/types/functions: Extends `BackgroundService`. Constructor validates configured table names and uses a single compactor thread. Important methods are `validateTables`, `suspend`, `resume`, `getCompactableTables`, `getNumCompactions`, `getTasks`, `compactTableAsync`, `compactFully`, and nested `CompactTask`.

Control flow and persistence: `validateTables` intersects configured names with `omMetadataManager.listTableNames`, skips invalid names with warnings, and fails initialization if none remain. `getTasks` creates a compaction task per valid table. Each task checks `suspended`, calls `CompactDBUtil.compactTable`, increments `numCompactions`, and returns a one-item task result.

Dependencies and integration: Integrated by OM service startup or admin compaction configuration. Uses `CompactDBUtil`, `OzoneManager`, and `OMMetadataManager`.

Risks and test signals: Bad configuration can fail startup when no tables are valid; compaction can affect IO latency. Tests should cover invalid table filtering, all-invalid failure, suspend/resume behavior, per-table task creation, compaction count, and async on-demand compaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/CompactionService.java -->
