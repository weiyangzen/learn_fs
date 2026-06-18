## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/SnapshotChainRepair.java

Purpose: offline OM repair command for corrupted snapshot predecessor links in `snapshotInfoTable`.

Important APIs and control flow: command `snapshot chain` takes a bucket URI, snapshot name, `--db`, required `--global-previous` UUID, and required `--path-previous` UUID. It opens RocksDB with latest options, locates the `snapshotInfoTable` column family, builds the `SnapshotInfo` key from bucket URI and snapshot name, loads the target snapshot, scans all snapshot IDs into a set, rejects self-references and nonexistent predecessor IDs, mutates the target `SnapshotInfo`, serializes it, and writes it back unless dry-run is set.

State and dependencies: mutates a single row in OM RocksDB. It depends on `BucketUri`, `SnapshotInfo` codec/table-key rules, managed RocksDB handles, and `StringCodec`.

Risks and test signals: validation checks existence of predecessor IDs but not complete acyclicity or ordering semantics. Running with OM active is unsafe. `TestSnapshotChainRepair` covers success/dry-run, self-reference rejection, nonexistent predecessor rejection, and write/no-write behavior.
