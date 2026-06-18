# sources/storage-engines/pebble/obsolete_files.go

Purpose: This file manages deletion of obsolete Pebble files and objects. It integrates the delete pacer, filesystem cleaners, object storage provider deletion, file-cache eviction, manifest/options retention, WAL recycling/deletion, and zombie object tracking.

Important APIs and types: Exported aliases expose `Cleaner`, `DeleteCleaner`, and `ArchiveCleaner`. `openDeletePacer` wires `deleteObsoleteFile` into `deletepacer`. `scanObsoleteFiles`, `disableFileDeletions`, `enableFileDeletions`, `deleteObsoleteFiles`, `maybeScheduleObsoleteObjectDeletion`, `mergeObsoleteFiles`, `objectInfo`, and `zombieObjects` implement DB cleanup logic.

Control flow: `scanObsoleteFiles` must run with `db.mu` and no active compaction/flush. It builds live file numbers from current versions and ingested flushables, scans the directory for old manifests/options, then scans `objProvider.List()` for table/blob objects no longer live. It records obsolete objects by placement and size when available. `deleteObsoleteFiles` respects deletion disablement, gets obsolete WALs, drains obsolete table/blob slices, retains the newest configured manifests, releases `db.mu`, prepares a deletion batch, evicts file-cache entries for table/blob files, and enqueues work to the delete pacer. `deleteObsoleteFile` uses the object provider for tables/blobs and the cleaner for other file types, then emits event listener callbacks.

State and persistence: Obsolete lists live in `d.mu.versions` until enqueued. Actual deletion/archive is asynchronous via delete pacer and cleaner/provider. `zombieObjects` tracks objects no longer in the latest LSM but still needed by iterators.

Dependencies and integration: DB open calls scan/delete after writing a new OPTIONS file. Version management and iterator lifecycle populate obsolete/zombie objects. Object storage provider abstracts local/remote placement.

Risks and test signals: Risks include deleting files still referenced by flushable ingests or iterators, path mistakes, unsorted retention lists, and remote ref cleanup behavior. Tests cover full-path stat regression and cleaner data-driven behavior.
