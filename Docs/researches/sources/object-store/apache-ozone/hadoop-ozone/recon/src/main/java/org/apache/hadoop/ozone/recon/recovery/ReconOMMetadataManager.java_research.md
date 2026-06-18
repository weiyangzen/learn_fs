## sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/recovery/ReconOMMetadataManager.java

Purpose: Recon extension of OM metadata manager for managing the local OM snapshot DB and providing Recon-specific listing/basic-key APIs.

Important APIs/types/functions: `updateOmDB`; `getLastSequenceNumberFromDB`; `isOmTablesInitialized`; volume and bucket listing/existence methods; `getOzoneConfiguration`; `getKeyTableBasic`; `createCheckpointReconMetadataManager`.

Control flow and state: interface only; implementation manages DB store refresh and direct table iteration. Extends `OMMetadataManager`, so callers can use normal OM metadata APIs plus Recon-specific snapshot lifecycle operations.

State and persistence: represents Recon's local RocksDB snapshot of OM metadata. Integrates with `DBCheckpoint`, `Table`, `BucketLayout`, OM helper types, and Recon API basic key info.

Risks: broad interface mixes lifecycle, listing, and factory behavior. Tests should target implementation behavior for snapshot replacement, sequence number, table initialization, and listing pagination.
