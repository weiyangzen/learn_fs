## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/FSORepairTool.java

Purpose: offline OM repair tool for disconnected FILE_SYSTEM_OPTIMIZED bucket trees. It finds reachable objects, pending-deletion objects, and truly orphaned FSO file/directory records, then moves orphaned records into deletion tables when not in dry-run.

Important APIs and control flow: `execute` requires OM offline and delegates to `Impl.run`. Inputs are `--db`, optional `--volume`, and optional `--bucket`. `Impl` opens the OM DB via `OMDBDefinition`, opens a temporary `temp.db` with `reachable` and `pendingToDelete` tables, iterates volumes/buckets, skips non-FSO buckets and buckets with snapshots, DFS-marks reachable directories from bucket roots, marks descendants of `deletedDirectoryTable` entries as pending deletion, scans directory/file tables, and repairs orphaned rows. `markFileForDeletion` deletes from `fileTable` and inserts `RepeatedOmKeyInfo` into `deletedTable`; `markDirectoryForDeletion` deletes from `directoryTable` and inserts a unique entry into `deletedDirectoryTable`.

State and dependencies: mutates OM RocksDB tables in batches; creates and deletes sibling `temp.db`; depends on OM DB codecs, FSO key format, `OMFileRequest`, and object IDs.

Risks and test signals: the tool must run after OM/Ratis state is flushed and skips snapshot buckets to avoid snapshot-chain side effects. Prefix scans and DFS can be expensive. Tests in this subset verify repair prompt behavior, not FSO classification itself.
