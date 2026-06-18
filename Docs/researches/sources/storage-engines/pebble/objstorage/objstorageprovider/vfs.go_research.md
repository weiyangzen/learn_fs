# sources/storage-engines/pebble/objstorage/objstorageprovider/vfs.go

Purpose: This file implements the local filesystem backend of the object storage provider, including hot-tier objects, optional cold-tier blob objects, metadata-file discovery, directory syncing, and local size/remove/open/create operations.

Important types and functions: `localSubsystem` stores open directory handles. `localLockedState` tracks hot/cold object change counters and cold-tier metadata files. `localPath`, `metaFileType`, `metaPath`, and `offsetFromMetaPath` format/parse object paths. `localOpenForReading`, `vfsCreate`, `localRemove`, `localInit`, `localClose`, `localSync`, `localSize`, and cold metadata map helpers are the core methods.

Control flow: `localInit` opens the hot directory, lists or uses an initial listing, records table/blob objects, then optionally opens/list cold tier and records cold objects unless a hot duplicate exists. It also scans hot-tier blob metadata files for cold blobs, deleting stray metadata files without matching objects. `vfsCreate` creates a syncing file, wraps it in `fileBufferedWritable`, and for cold blobs wraps in a cold writable. `localOpenForReading` opens a VFS readable and, for cold blobs with known hot metadata, returns a cold readable overlay.

State and persistence: Objects are files in hot or cold directories. Cold blob metadata can be dual-written into hot-tier `.blobmeta.<offset>` files. Change counters avoid unnecessary directory syncs when only remote objects changed; `localSync` syncs directories whose counters advanced.

Dependencies and integration: Provider create/open/remove/size/list paths call these methods. Cold-tier wrappers live in adjacent files outside this subset. `FSCleaner` handles local deletion/archive semantics.

Risks and test signals: Risks include duplicate hot/cold file numbers, stale metadata files, unsynced directory entries, and unsupported cold-tier file types. Provider data-driven tests cover local, cold-tier, cold metadata, local readahead, and remove/list behavior.
