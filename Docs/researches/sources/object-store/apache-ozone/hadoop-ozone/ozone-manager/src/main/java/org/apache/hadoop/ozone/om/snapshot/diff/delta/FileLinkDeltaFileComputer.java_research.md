## sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/snapshot/diff/delta/FileLinkDeltaFileComputer.java

Purpose: abstract base for delta computers that materialize selected SST files as hard links in a temporary directory.

Important APIs and types: final `getDeltaFiles` resolves bucket table prefixes and delegates to abstract `computeDeltaFiles`; `createLink` creates unique numbered hard links preserving file extension; `getLocalDataProvider`, `getSnapshot`, `getActiveMetadataManager`, `updateActivity`, and `close` support subclasses.

Control flow: constructor creates the temp directory. `getDeltaFiles` maps subclass optional results to collection values and throws if no result can be computed. `createLink` loops on `FileAlreadyExistsException` using an atomic counter. `close` deletes the temp directory if present.

State and persistence: state is temporary filesystem hard links and an in-memory link counter. No durable metadata is written.

Dependencies and integration: base for `RDBDifferComputer`, `FullDiffComputer`, and `CompositeDeltaDiffComputer`; integrates with `OmSnapshotManager`, active metadata table-prefix lookup, and snapshot local data manager.

Risks and test signals: hard links require same filesystem and sufficient permissions; callers rely on deletion not touching source SSTs. Tests should cover unique link creation, extension preservation, missing source filename errors, optional-empty to IOException conversion, table-prefix lookup, and recursive cleanup.
