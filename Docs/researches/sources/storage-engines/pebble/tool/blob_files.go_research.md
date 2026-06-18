# sources/storage-engines/pebble/tool/blob_files.go

## Purpose
This file provides manifest-derived blob-file mapping support for Pebble debug tooling. SSTables that reference separated values do not directly encode every physical blob file detail needed for reading; this helper loads manifests to map table numbers to blob references and blob file IDs to physical disk file numbers, then exposes a `sstable.TableBlobContext`.

## Important APIs, Types, and Functions
The main type is `blobFileMappings`, containing `references`, `physicalFiles`, a `blob.ValueFetcher`, a `debugReaderProvider`, and stderr for warnings. Public-style methods are `LoadValueBlobContext`, `Lookup`, and `Close`. The constructor `newBlobFileMappings` reads a list of manifest `fileLoc` values and builds all mappings.

`LoadValueBlobContext` returns `sstable.TableBlobContext{ValueFetcher, References}` for a table number. `Lookup` implements `base.BlobFileMapping`, returning a `base.ObjectInfoLiteral` for the newest physical file associated with a blob file ID. `Close` combines cleanup for the value fetcher and object provider.

## Control Flow
`newBlobFileMappings` opens an object storage provider for the DB directory, initializes maps, initializes the `blob.ValueFetcher` with the mapping object and a cached reader count from `blob.SuggestedCachedReaders(5)`, then iterates over manifest files. Each manifest is opened through the VFS, wrapped in `record.NewReader`, decoded record-by-record as `manifest.VersionEdit`, and inspected for `NewTables` and `NewBlobFiles`. New table entries populate table-number-to-blob-references mapping. New blob file entries append unique physical file numbers per blob file ID.

Errors while reading a manifest are written to stderr and do not abort construction. The comments explain why: a manifest rotation may leave some manifests unreadable while other manifests still provide enough information for debug reads.

## State and Persistence Behavior
This code is read-only against manifests and object storage, but it builds in-memory state that must be closed. The `physicalFiles` map intentionally accumulates every physical file number ever observed for each logical blob file ID rather than only the latest manifest state. `Lookup` returns the last physical file number in that accumulated slice and warns if multiple physical files were seen.

## Dependencies and Integration Points
Dependencies include `manifest.VersionEdit`, `manifest.BlobReferences`, `base.BlobFileID`, `base.ObjectInfoLiteral`, `objstorageprovider`, `record.Reader`, `sstable.TableBlobContext`, `blob.ValueFetcher`, `block.ReadEnv`, and `vfs`. The mapping is used by SSTable debug/read tooling that needs to fetch blob-separated values while scanning tables.

## Risks and Edge Cases
The main correctness risk is stale or ambiguous blob file identity. The file chooses the last physical file when several are observed and logs a warning, but it does not verify file existence or bounds. Manifest read failures are deliberately non-fatal, which helps debugging live/rotating DBs but can leave missing mappings. The cached reader count of 5 is arbitrary and may not match large manifests or high read amplification, though this is acceptable for a debug tool. `Close` must be called to release object provider and fetcher resources.

## Test Signals
Direct tests are not in this file, but `tool/blob_test.go` may exercise separated-value reads indirectly if datadriven blob fixtures require manifest mapping. Runtime warning output for multiple physical files or manifest read errors is an important diagnostic signal.
