# sources/user-network-fs/rclone/backend/compress/zstd_handler.go

## Purpose
This file implements the zstd-specific `compressionModeHandler`. It mirrors gzip handler responsibilities using the package's seekable zstd helper for compression metadata and offset reads.

## Important APIs, types, and functions
`zstdModeHandler` implements all handler methods. `isCompressible` compresses a sample with `NewWriterSzstd` at default speed and compares original/compressed ratio. `newObjectGetOriginalSize` requires `CompressionMetadataZstd`. `openGetReadCloser` uses `NewReaderAtSzstd` for nonzero offsets and `zstd.NewReader` for full reads from offset zero. `putCompress` streams plaintext through a zstd writer goroutine, computes original MD5, optionally hashes compressed bytes for transfer verification, uploads with `f.rcat`, waits for `SzstdMetadata`, and builds `ObjectMetadata`.

## Control flow
Upload uses `io.Pipe` and a goroutine that creates `NewWriterSzstd` with configured encoder level, copies plaintext, closes the writer and pipe, then publishes metadata/errors on a channel. The main goroutine uploads the compressed pipe reader, receives the compression result, removes partial output on compression failure, and verifies underlying hash if available. Reads use metadata-backed seeking for ranged opens and plain streaming decoder for offset-zero reads.

## State and persistence behavior
Zstd metadata is stored in `ObjectMetadata.CompressionMetadataZstd`, including uncompressed size and block offsets. The stored data filename uses original size and `.zst`. Metadata MD5 is over the original plaintext. Optional hash verification validates the compressed object as stored by the underlying backend.

## Dependencies and integration points
This handler depends on `klauspost/compress/zstd`, the local seekable zstd helper, rclone accounting, chunkedreader, and hash utilities. It is selected from `compress.go` when mode is `zstd`.

## Risks and edge cases
Compression level is cast directly to `zstd.EncoderLevel`, so config validation must ensure values are meaningful. Partial upload cleanup is less detailed than the gzip handler in some error paths. Offset reads inherit concurrency and metadata risks from `szstd_helper.go`. Compressibility is sampled using default speed rather than the configured level. As with gzip, `newMetadata` panics if called with the wrong metadata type.

## Test signals
Zstd mode is covered by generic local `fstests` in `compress_test.go`, but there are no focused unit tests for seek metadata, range reads, zstd-level mapping, or corruption behavior.
