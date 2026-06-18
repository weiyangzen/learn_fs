# Research: sources/storage-engines/rocksdb/include/rocksdb/utilities/checkpoint.h

- **Purpose:** Declares `Checkpoint`, an API for creating openable point-in-time snapshots and exporting live SST files for a column family.
- **Important APIs/types/functions:** `Checkpoint::Create(DB*, Checkpoint**)`, `CreateCheckpoint(checkpoint_dir, log_size_for_flush, sequence_number_ptr)`, `ExportColumnFamily(handle, export_dir, metadata)`, and destructor.
- **Control flow:** Users create a `Checkpoint` bound to a DB, then call `CreateCheckpoint()` with a non-existing absolute destination. RocksDB flushes depending on WAL size and 2PC rules, hard-links SST/blob files when possible, copies files otherwise, and always copies required metadata such as MANIFEST. `ExportColumnFamily()` flushes and exports live SSTs for a CF with metadata.
- **State and persistence:** Checkpoints are durable directory snapshots that can be opened as DBs. Exported CF directories contain hard links or copies plus export/import metadata. Optional sequence-number output identifies a sequence guaranteed to be included.
- **Dependencies:** Depends on `DB`, column-family handles, live-file metadata, export/import metadata, and `Status`.
- **Integration points:** Used by backup workflows, snapshot export/import, testing, and operational cloning.
- **Risks:** If WAL writing is disabled and flush is not forced appropriately, the checkpoint may miss recent memtable data. Multi-directory DB paths are not supported for checkpoint/export. Destination directories must not already exist.
- **Test signals:** Tests should cover hard-link versus copy fallback, flush threshold behavior, sequence-number output, 2PC flush behavior, unsupported multi-path DBs, export metadata validity, and opening a created checkpoint.
