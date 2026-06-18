<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java

Purpose: Picocli grouping command for OM snapshot-related admin operations. Currently it exposes snapshot defragmentation.

Important APIs and types: Picocli `@Command` and `DefragSubCommand`.

Control flow: No methods. Picocli routes `ozone admin om snapshot defrag` to the child command.

State and persistence behavior: No state or persistence in the grouping class.

Dependencies and integration points: Registered as a child of `OMAdmin` and names the snapshot admin namespace.

Risks: Passive registration only; missing child registration would hide snapshot operations.

Test signals: CLI command discovery/help should include `defrag` under `om snapshot`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/ozone/admin/om/snapshot/SnapshotSubCommand.java -->
