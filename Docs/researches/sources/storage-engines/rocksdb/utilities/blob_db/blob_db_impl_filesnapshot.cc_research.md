## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_impl_filesnapshot.cc`

Purpose: implements BlobDB live-file and deletion snapshot APIs used by backup, checkpoint, replication, and storage inventory paths. It extends base DB live-file output with blob files and coordinates blob-file deletion disable/enable with the base DB.

Important APIs and functions: `DisableFileDeletions()` calls `db_impl_->DisableFileDeletions()` and then increments `disable_file_deletions_` under `delete_file_mutex_`. `EnableFileDeletions()` calls the base enable path and decrements the BlobDB disable counter. `GetLiveFiles()` locks BlobDB metadata, delegates to `db_->GetLiveFiles()`, and appends blob file names relative to the DB root. `GetLiveFilesMetaData()` appends `LiveFileMetaData` for each blob file, including size, relative name, file number, TTL-derived `oldest_ancester_time`, and default CF name. `GetLiveFilesStorageInfo()` appends `LiveFileStorageInfo` entries with directory, relative filename, file type `kBlobFile`, size, and `trim_to_size`.

Control flow: all live-file enumeration begins with a read lock on `mutex_` to avoid concurrent blob file registration/deletion while the base DB and blob file lists are combined. Deletion disable is two-layered: the base DB is disabled first, then BlobDB deletion state is incremented while holding `delete_file_mutex_` so `DeleteObsoleteFiles()` cannot race through the gap.

State and persistence behavior: no new persistent data is written. The code exposes the current in-memory `blob_files_` map as file snapshots and blocks physical deletion by increasing `disable_file_deletions_`. `DeleteObsoleteFiles()` in the implementation honors that counter, so obsolete files remain listed until re-enabled and deleted.

Dependencies and integration: relies on `BlobFileName`, logging, `ColumnFamilyHandleImpl` casts, base DB live-file APIs, `LiveFileMetaData`, `LiveFileStorageInfo`, and BlobDB locking fields declared in `blob_db_impl.h`.

Risks: holding BlobDB `mutex_` around base DB live-file calls keeps snapshots consistent but can increase contention. `EnableFileDeletions()` only decrements if positive; mismatched enable/disable calls can leave deletions enabled earlier or later than intended depending on base DB state. The code assumes BlobDB supports only the default CF when filling metadata.

Test signals: `GetLiveFilesMetaData` in `blob_db_test.cc` verifies blob metadata names, file numbers, TTL ancestor time, CF names, live-file list appends, and storage-info entries. `DisableFileDeletions` verifies nested disable counts block and later permit obsolete blob file deletion.
