# sources/storage-engines/pebble/objstorage/objstorageprovider/remoteobjcat/catalog.go

Purpose: This file implements the durable local catalog of remote objects known to a Pebble store. The catalog is an append-only record log of `VersionEdit`s with atomic marker files for selecting the current catalog file.

Important types and functions: `Catalog` owns filesystem handles, creator ID, object map, marker, active catalog file/writer, and rotation helper under a mutex. `RemoteObjectMetadata` is the durable representation of a remote object. `CatalogContents` is returned by `Open`. `SetCreatorID`, `ApplyBatch`, `Checkpoint`, and `Close` are the public mutation/lifecycle APIs. `Batch` groups `AddObject` and `DeleteObject` operations.

Control flow: `Open` locates the marker, loads the selected catalog file if present, removes obsolete marker files, and returns sorted contents. `SetCreatorID` writes a creator-ID edit and refuses changes. `ApplyBatch` validates additions/deletions, writes the edit durably, then mutates the in-memory map. `writeToCatalogFileLocked` rotates on first write or when the record writer exceeds 1 MiB and `RotationHelper` says a snapshot is worthwhile. New catalog files write a full snapshot, sync the directory, move the marker, then remove the previous file.

State and persistence: Persistence depends on record flush plus file sync for each edit and atomic marker movement for rotation. The catalog stores remote object metadata, not object data or ref markers. `Checkpoint` copies the active catalog and marker into another FS/dir.

Dependencies and integration: The provider calls this during `remoteInit`, `sharedSync`, `SetCreatorID`, and checkpointing. It depends on `record`, `atomicfs.Marker`, `vfs`, and `VersionEdit`.

Risks and test signals: Risks include marker/catalog crash ordering, duplicate/deleted-object assertions, partial/corrupt record handling, and catalog-file cleanup. Tests cover data-driven open/batch/rotation/list/close behavior with open-file tracking.
