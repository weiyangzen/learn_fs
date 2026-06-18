# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/repair/om/TestFSORepairTool.java

## Purpose
`TestFSORepairTool` validates the offline OM `fso-tree` repair command against connected, disconnected, empty, non-FSO, filtered, and pending-deletion FSO namespace trees. It verifies dry-run reporting, repair mutations, idempotence, alternate DB directory names, and cluster restart after repair.

## Important APIs, Types, and Functions
The test uses `OzoneRepair().getCmd()` with `om fso-tree --db ...`, `--dry-run`, `--volume`, and `--bucket`. It constructs namespace state through OFS `FileSystem`, `ObjectStore`, and bucket layout APIs, then deliberately corrupts OM RocksDB tables by deleting entries from `directoryTable` or moving entries to `deletedDirTable` using `OMFileRequest.getOmKeyInfo`. Report expectations use `FSORepairTool.Report` and `ReportStatistics`.

## Control Flow, State, and Persistence
`setup` starts a mini cluster, initializes OFS, builds several trees, creates OBS and legacy buckets for skip coverage, captures stdout/stderr, records the OM DB path, and stops the OM before executing the offline tool. Ordered tests first run dry-run/report cases, then run full repair, then run repair again to verify no remaining orphaned objects, and finally restart the OM and count metadata table entries. Helper builders create reachable trees, disconnected orphan trees, empty trees, and trees where a parent is already in the deleted directory table so descendants are classified as unreachable pending deletion rather than orphaned.

## Dependencies and Integration Points
This file integrates the repair CLI, OM RocksDB schema, FSO directory and key tables, deleted directory/deleted key tables, OFS behavior, picocli confirmation input, non-FSO bucket filtering, and mini-cluster restart validation.

## Risks and Test Signals
Risks include direct RocksDB table mutation bypassing normal invariants, test order coupling, stdout formatting brittleness, and offline repair assumptions requiring OM shutdown. Signals include exact report serialization, warning/error text for filters, skip messages for non-FSO buckets, post-repair orphan counts, idempotent second repair, and table counts after OM restart.
