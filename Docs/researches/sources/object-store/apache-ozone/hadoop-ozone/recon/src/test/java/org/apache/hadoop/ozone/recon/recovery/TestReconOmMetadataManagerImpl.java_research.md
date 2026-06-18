# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/recovery/TestReconOmMetadataManagerImpl.java

## Purpose
Validates `ReconOmMetadataManagerImpl` startup and snapshot replacement behavior using real OM metadata checkpoints. It proves Recon can open an OM DB snapshot, expose OM metadata tables, and replace an existing opened snapshot DB while closing the old `DBStore`.

## Important APIs, types, and functions
- Uses `OmMetadataManagerImpl` to create a source OM RocksDB and `ReconOmMetadataManagerImpl` as the Recon-side consumer.
- Writes `OmVolumeArgs`, `OmBucketInfo`, and `OmKeyInfo` directly into OM metadata tables.
- Uses `DBCheckpoint`, `DBStore`, `OZONE_OM_DB_DIRS`, `OZONE_RECON_OM_SNAPSHOT_DB_DIR`, `FileUtils.copyDirectory`, and `ReconUtils`.

## Control flow
`testStart` creates a source OM DB, writes one volume, one bucket, and two keys, takes a checkpoint, renames the checkpoint directory to an OM snapshot-style name, copies the parent snapshot area into Recon's snapshot directory, starts `ReconOmMetadataManagerImpl`, and verifies tables and entries are readable. `testUpdateOmDB` starts Recon without a snapshot table initialized, calls `updateOmDB` with a checkpoint, verifies the metadata appears, then updates with another checkpoint and asserts the previous store was closed.

## State and persistence behavior
Persistent state lives in real RocksDB metadata directories under JUnit temp paths. The source OM DB contains volume, bucket, and default-layout key table entries. Recon should not expose tables before a snapshot update in the second test, should open the checkpoint atomically enough for reads afterward, and should close superseded DB handles on replacement.

## Dependencies and integration points
This is the recovery-layer bridge between OM metadata checkpoints and Recon's metadata reader. It depends on OM table key formatting, default bucket layout key tables, RocksDB checkpoint creation, and Recon snapshot directory configuration.

## Risks and edge cases
The tests use direct table writes rather than OM request processing, so they verify snapshot consumption but not OM transaction semantics. Snapshot directory copying and rename behavior may be platform-sensitive. Coverage is limited to default bucket layout and two keys.

## Test signals
Signals are non-null Recon volume, bucket, and key table lookups after startup/update, null table before first update, non-null new checkpoint location, and `current.isClosed()` after replacing the opened Recon OM DB.
