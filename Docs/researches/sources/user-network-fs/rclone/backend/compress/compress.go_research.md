# sources/user-network-fs/rclone/backend/compress/compress.go

## Purpose
This file implements the `compress` wrapper backend, which stores each logical object on an underlying remote as a data object plus JSON metadata. It can compress data with gzip or zstd when heuristics show sufficient benefit, fall back to uncompressed storage, and expose original names, sizes, MIME type, and MD5 through rclone interfaces.

## Important APIs, types, and functions
`Options` configures wrapped remote, compression mode, level, and RAM cache limit. `Fs` wraps an underlying `fs.Fs`, selected mode id, mode handler, and feature set. `compressionModeHandler` defines the algorithm-specific operations used by this file. `ObjectMetadata` records `Mode`, original `Size`, original `MD5`, MIME type, and per-algorithm metadata. `Object` wraps the data object and metadata object; metadata may be lazy-loaded. `ObjectInfo` overrides remote and size for underlying writes.

Important helpers include `compressionModeFromName`, `makeMetadataName`, `makeDataName`, `processFileName`, `checkCompressAndType`, `verifyObjectHash`, `rcat`, `putCompress`, `putUncompress`, `putMetadata`, and `putWithCustomFunctions`.

## Control flow
`NewFs` parses the wrapped remote, checks whether the requested path is a metadata-backed file or a directory, selects a handler, masks features with the wrapped fs, and disables `PutStream` unless server-side move/copy is possible. Listing delegates to the wrapped remote and filters out metadata files; data file names are parsed into logical object names and sizes. `NewObject` reads `<remote>.json`, extracts metadata, computes the expected data object name, and wraps both objects.

`Put` checks for an existing logical object, samples up to `heuristicBytes` for MIME/compressibility, uploads either compressed or uncompressed data, then writes metadata. `PutStream` performs the same but uploads compressed streams under a temporary unknown-size name and moves them to the final size-encoded name once compression metadata is known. Updates preserve server-side versioning when possible, but may delete the old data object when the encoded data filename changes. `Open` lazy-loads metadata, passes uncompressed files straight through, and uses `chunkedreader` plus algorithm-specific random-access readers for compressed files.

## State and persistence behavior
For each logical file, the backend persists `<name>.json` metadata and either `<name>.<base64-original-size>.gz`, `<name>.<base64-original-size>.zst`, or `<name>.bin`. Metadata is authoritative for logical size, MD5, MIME type, mode, and compression seek metadata. Partial upload failure paths attempt to remove data or metadata to avoid orphaned objects, but data/metadata two-phase writes can still leave orphaned files if cleanup fails. Uncompressed files store logical size as the underlying object size rather than in the filename.

## Dependencies and integration points
The backend uses rclone wrapping, accounting, chunkedreader, list, object, operations, hash, and metadata interfaces. Compression-specific behavior is delegated to handler files. MIME detection uses `gabriel-vasile/mimetype`. Gzip metadata uses `buengese/sgzip`; zstd uses local helper code and `klauspost/compress/zstd`.

## Risks and edge cases
`compressionModeFromName` treats unknown modes as uncompressed, so the `unknownModeHandler` is not normally selected through config. `processEntries` ignores parse failures except for logging, so malformed stored data objects disappear from listings. `ListR` assumes the wrapped fs exposes `Features().ListR`; if not, it can panic unless feature masking prevents calls. `rcat` defers close/remove on `tempFile` before checking `os.CreateTemp` error; if temp creation fails, dereferencing `tempFile` in the defer would panic. Metadata upload failure cleanup returns removal errors ahead of metadata errors, which can hide the original cause. `SetMetadata` writes metadata to the data object, while `Metadata` reads from the metadata object, creating possible inconsistency.

## Test signals
`compress_test.go` runs generic `fstests` for configured remotes and local gzip/zstd wrappers. It marks several optional methods unimplementable, including `PutStream`, even though the backend conditionally supports it. There is no targeted unit coverage for filename parsing, metadata consistency, `rcat` spooling, update/delete sequencing, MIME detection, or malformed metadata handling.
