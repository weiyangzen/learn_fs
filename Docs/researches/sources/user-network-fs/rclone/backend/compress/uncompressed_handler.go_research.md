# sources/user-network-fs/rclone/backend/compress/uncompressed_handler.go

## Purpose
This file defines the handler used for the nominal uncompressed compression mode. It mainly disables compression-specific behavior and passes object opens through to the underlying object.

## Important APIs, types, and functions
`uncompressedModeHandler` implements `compressionModeHandler`. `isCompressible` always returns false. `newObjectGetOriginalSize` returns zero. `openGetReadCloser` delegates directly to `o.Object.Open`. `processFileNameGetFileExtension` returns an empty extension. `putCompress`, `putUncompressGetNewMetadata`, and `newMetadata` return unsupported-mode errors or nil.

## Control flow
The handler prevents compression by returning `compressible=false`. If an object metadata mode is uncompressed, `compress.go` already opens the wrapped object directly before invoking handler-specific compressed open logic. The unsupported methods are defensive stubs for paths that should not be used in normal uncompressed operation.

## State and persistence behavior
No algorithm metadata is produced by this handler. In the main compress backend, uncompressed persisted data is expected to use the `.bin` suffix plus a JSON metadata file produced by the active gzip or zstd handler's `putUncompressGetNewMetadata` when a file is not worth compressing. This handler itself does not produce metadata for that path.

## Dependencies and integration points
It depends only on shared rclone `fs` and `chunkedreader` types and the `compress` package's `Object` type. It is selected when `compressionModeFromName` returns `Uncompressed`, which currently includes any mode string other than `gzip` or `zstd`.

## Risks and edge cases
Because unknown config names map to `Uncompressed`, this handler may be selected for typoed modes and then fail on upload with `unsupported compression mode` rather than falling back to a full uncompressed wrapper. `newObjectGetOriginalSize` returning zero can make `NewObject` look for `<remote>.bin` based on size zero if metadata mode is uncompressed and this handler is active. The intended uncompressed fallback for incompressible files is actually implemented by gzip/zstd handlers, not this one.

## Test signals
No direct tests cover this handler. The generic compress tests configure only gzip and zstd modes.
