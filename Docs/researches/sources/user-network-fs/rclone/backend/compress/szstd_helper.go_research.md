# sources/user-network-fs/rclone/backend/compress/szstd_helper.go

## Purpose
This file provides seekable zstd support for the compress backend. It defines metadata, writer, and reader abstractions over the seekable zstd format so compressed zstd objects can support ranged logical reads.

## Important APIs, types, and functions
`SzstdMetadata` stores block size, uncompressed size, and cumulative compressed block offsets. `SzstdWriter` wraps a `klauspost/compress/zstd.Encoder` and `a1ex3/zstd-seekable-format-go` concurrent writer. `NewWriterSzstd` initializes both. `Write` chunks input into `szstdChunkSize` blocks, updates uncompressed size, and records cumulative compressed offsets through a write callback. `Close` closes the seekable writer and encoder. `GetMetadata` returns the recorded metadata.

`SzstdReaderAt` wraps a seekable zstd reader, zstd decoder, metadata, current position, and mutex. `NewReaderAtSzstd` creates the reader and seeks to an initial logical offset. `Seek`, `Read`, `ReadAt`, and `Close` expose random-access reads and cleanup.

## Control flow
`Write` initializes `BlockData` lazily with a zero offset, then passes a frame source callback to `WriteMany`. The callback returns sequential chunks from the caller's `p` buffer and updates original size; the write callback appends cumulative compressed offsets. `ReadAt` translates an uncompressed byte range into block indexes, launches bounded parallel goroutines to read and decode compressed blocks, collects results by block index, copies requested subranges into the caller buffer, and returns the total bytes read.

## State and persistence behavior
`SzstdMetadata` is persisted inside the compress metadata JSON and is required for offset reads. `BlockData` is cumulative, where each pair of adjacent entries identifies one compressed block. Runtime state includes decoder/reader handles and current read position protected by a mutex.

## Dependencies and integration points
This helper is used by `zstd_handler.go`. It depends on `github.com/a1ex3/zstd-seekable-format-go/pkg`, `github.com/klauspost/compress/zstd`, Go `runtime` for concurrency bounds, and synchronization primitives.

## Risks and edge cases
`Write` only chunks within each `Write(p)` call; if the compressor receives many small writes, block boundaries and metadata depend on upstream copy behavior. `ReadAt` shares a single `zstd.Decoder` across parallel goroutines calling `DecodeAll`, which may not be concurrency-safe. It also returns `nil` error even if fewer bytes than requested are read near EOF, so callers must interpret byte counts carefully. Metadata corruption can cause invalid block offsets, large allocations, or decode failures. `Seek` and `Read` use the underlying seekable reader while `ReadAt` also uses it concurrently, so mixed access patterns should be treated cautiously.

## Test signals
There are no direct unit tests for this helper in the listed files. Zstd behavior is indirectly exercised by generic compress zstd integration tests, but parallel `ReadAt`, metadata corruption, and small-write block layout are not explicitly covered.
