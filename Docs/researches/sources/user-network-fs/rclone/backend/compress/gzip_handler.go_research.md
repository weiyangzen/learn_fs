# sources/user-network-fs/rclone/backend/compress/gzip_handler.go

## Purpose
This file implements the gzip-specific `compressionModeHandler`. It decides compressibility, compresses upload streams into seekable gzip, constructs gzip metadata, and opens compressed objects for normal or offset reads.

## Important APIs, types, and functions
`gzipModeHandler` implements all handler methods. `isCompressible` compresses a sample with `sgzip.DefaultCompression` and compares original/compressed ratio to `minCompressionRatio`. `newObjectGetOriginalSize` reads `CompressionMetadataGzip.Size`. `openGetReadCloser` uses `sgzip.NewReaderAt` when offset is nonzero and `sgzip.NewReader` otherwise, then wraps with optional `io.LimitReader`. `putCompress` builds a compression goroutine around `io.Pipe`, records original MD5, optionally hashes compressed bytes using an underlying-supported hash, uploads via `f.rcat`, reads gzip metadata from the goroutine, validates the compressed hash, and returns data object plus metadata. `newMetadata` builds `ObjectMetadata`.

## Control flow
Upload flow unwraps accounting, tees plaintext into an MD5 hasher, compresses in a goroutine, wraps the pipe reader, optionally tees compressed bytes into a destination hash verifier, and streams/spools via `rcat`. Once upload completes, it waits for the compression result channel, removes partial output on compression errors, then records original MD5 and seek metadata.

## State and persistence behavior
Gzip metadata is stored in `ObjectMetadata.CompressionMetadataGzip` and includes original size plus seek data from `sgzip`. The persisted data object name includes original size and `.gz`. MD5 stored in metadata is over original uncompressed content, while optional transfer hash verification covers compressed bytes as stored on the underlying remote.

## Dependencies and integration points
The handler depends on `github.com/buengese/sgzip`, rclone accounting, chunkedreader, hash utilities, and the shared `compress.Fs` persistence helpers. It is selected by `compress.go` when mode is `gzip`.

## Risks and edge cases
The goroutine writes an error to an unbuffered channel after closing the pipe; if upload fails before the goroutine can send, ordering must avoid leaks. `newMetadata` panics on wrong metadata type, so all caller paths must preserve the handler contract. Compressibility is estimated on only the sampled bytes and at default compression, not necessarily the configured level. Offset reads rely on correct sgzip metadata and chunkedreader behavior.

## Test signals
Coverage is indirect through gzip-mode `fstests` in `compress_test.go`; no unit test directly validates gzip metadata, random-access reads, error cleanup, or ratio thresholds.
