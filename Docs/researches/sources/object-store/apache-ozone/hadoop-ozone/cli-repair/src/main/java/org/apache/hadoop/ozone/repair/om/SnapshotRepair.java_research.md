## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotRepair.java

Purpose: grouping command for snapshot-related OM repair operations.

Important APIs and control flow: picocli command `snapshot` registers `SnapshotChainRepair` as a subcommand. It does not implement execution logic itself.

State and dependencies: no runtime state. It depends only on picocli and the snapshot repair command class.

Risks and test signals: a metadata-only class, so risk is subcommand registration drift. `TestSnapshotChainRepair` exercises the registered path through `OzoneRepair` using `om snapshot chain`.
