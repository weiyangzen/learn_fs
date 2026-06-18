# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/tasks/TestOMDBUpdatesHandler.java

Purpose: Tests `OMDBUpdatesHandler`, the RocksDB write-batch decoder that turns OM metadata WAL updates into typed `OMDBUpdateEvent` instances for Recon tasks.

Important APIs and control flow: `setUp` creates separate source OM and Recon OM metadata managers. Tests write volumes, keys, delegation tokens, deleted entries, file table rows, deleted table rows, and directory rows into source OM DB, then `getBytesFromOmMetaManager` reads RocksDB updates via `getUpdatesSince`, captures `WriteBatch` bytes, and `captureEvents` iterates each batch through `OMDBUpdatesHandler`. Assertions verify PUT, UPDATE, DELETE, key/value type decoding, old-value lookup from Recon OM DB, and same RocksDB key strings across different tables.

State and persistence behavior: Source OM DB supplies WAL mutations; Recon OM DB is used as previous-state reference for old values and DELETE value recovery. Nonexistent DELETE operations are intentionally ignored because no old value can be resolved. Same-key events in file/deleted/directory tables must remain distinct by table to avoid class casts and event loss.

Dependencies and integration points: Uses `OmMetadataManagerImpl`, `RDBStore`, `RocksDatabase`, `ManagedTransactionLogIterator`, `WriteBatch`, `OMDBDefinition`, and OM helper value types (`OmVolumeArgs`, `OmKeyInfo`, `RepeatedOmKeyInfo`, `OmDirectoryInfo`, `OzoneTokenIdentifier`).

Risks and test signals: Strong signal for WAL parsing and type-safe event construction. Risks include assumptions about WAL sequence offsets, RocksDB write order, and random data sizes. Duplicate-key coverage is especially important for FSO paths where table identity is part of event identity.
