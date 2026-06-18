## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOmMetadataManagerImpl.java

Purpose: Recon implementation of OM metadata manager backed by local OM snapshot RocksDB stores.

Important APIs/types/functions: constructors; `createCheckpointReconMetadataManager`; `start`; `updateOmDB`; `getLastSequenceNumberFromDB`; `isOmTablesInitialized`; `getKeyTableBasic`; `listVolumes`; `volumeExists`; `listBucketsUnderVolume`; `getOzoneConfiguration`; private `initializeNewRdbStore` and `listAllBuckets`.

Control flow: `start` locates last known OM snapshot and initializes a DB store. `updateOmDB` deletes the old DB directory, initializes the new store, and closes the previous store if replaced. Listing methods iterate tables directly, not through OM cache, handling null tables with empty results. Bucket listing supports all-bucket mode, volume existence checks, start-bucket skipping, prefix seek, and max limits.

State and persistence: owns current `DBStore` inherited from `OmMetadataManagerImpl`, `omTablesInitialized`, config, and `ReconUtils`. Reads RocksDB metadata snapshots and may delete old snapshot directories. Integrates with OM DB definitions, table codecs, Recon snapshot directory config, and namespace/Recon APIs.

Risks: `initializeNewRdbStore` catches `IOException` internally and does not rethrow, so `updateOmDB` may silently leave no initialized store after logging. Deleting the old DB before successful initialization can lose last good local snapshot. `getLastSequenceNumberFromDB` casts store to `RDBStore`. Tests should cover startup without snapshot, checkpoint factory path validation, update failure, old-store close/delete ordering, list pagination, null tables, FSO/basic key table selection, and sequence-number IOException.
