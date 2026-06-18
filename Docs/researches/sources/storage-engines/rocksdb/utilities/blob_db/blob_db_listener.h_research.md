## `sources/storage-engines/rocksdb/utilities/blob_db/blob_db_listener.h`

Purpose: defines event listeners that connect base DB flush/compaction events back into BlobDB state. They keep blob files durable before flush and keep size and GC mapping metadata current after flushes and compactions.

Important APIs and types: `BlobDBListener` implements `OnFlushBegin`, `OnFlushCompleted`, `OnCompactionCompleted`, `Name`, and `kClassName`. `BlobDBListenerGC` extends it and overrides completed flush/compaction callbacks to invoke GC mapping updates. Both store a raw `BlobDBImpl*`.

Control flow: on flush begin, BlobDB syncs currently open blob files with `WriteOptions(Env::IOActivity::kFlush)` before the base DB flush publishes SSTs containing blob indexes. On flush completion and compaction completion, the base listener updates the live SST size used by `max_db_size` accounting. The GC listener then processes `FlushJobInfo` or `CompactionJobInfo` to link or unlink SST file numbers from oldest blob file numbers and mark unreferenced non-TTL blob files obsolete.

State and persistence behavior: listeners do not persist directly except through `SyncBlobFiles()` on flush begin. They mutate `live_sst_size_`, `flush_sequence_`, SST link sets inside `BlobFile`, and obsolete file lists through `BlobDBImpl`.

Dependencies and integration: integrates with RocksDB `EventListener`, `FlushJobInfo`, `CompactionJobInfo`, and BlobDB implementation private methods. `BlobDBImpl::Open()` installs either this listener or the GC variant depending on `enable_garbage_collection`.

Risks: callbacks use a raw DB implementation pointer and must not outlive `BlobDBImpl`; `CloseImpl()` closes the base DB before clearing `db_impl_` to stop listener and compaction-filter calls. `OnFlushBegin()` ignores sync errors via `PermitUncheckedError()`, so a durability failure is logged inside lower layers but not propagated through the callback. Locking can race with writes if `write_mutex_` ordering changes.

Test signals: BlobDB tests exercise listener effects through GC mapping maintenance, live SST size updates, sync-before-close counters, and max-size accounting.
