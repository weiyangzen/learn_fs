# sources/user-network-fs/rclone/fs/chunkedreader/chunkedreader.go

Purpose: defines the public chunked reader abstraction and chooses sequential or parallel implementations for reading an `fs.Object` in ranges.

Important APIs/types/functions: package errors `ErrorFileClosed` and `ErrorInvalidSeek`; interface `ChunkedReader` combining `io.Reader`, `io.Seeker`, `io.Closer`, `fs.RangeSeeker`, and `Open`; constructor `New(ctx, o, initialChunkSize, maxChunkSize, streams)`.

Control flow: `New` normalizes chunk sizes. `initialChunkSize <= 0` disables chunking by setting `-1`; `maxChunkSize` below initial is raised to initial unless `-1`; negative stream count becomes zero. It chooses sequential mode for streams <= 1 or unknown object size, otherwise parallel mode.

State and persistence behavior: no persistent state in this file. It determines initial runtime state for `sequential` or `parallel` readers.

Dependencies and integration points: depends on `fs.Object`, `fs.RangeSeeker`, and standard IO interfaces. Used by multi-thread downloads and backends that benefit from ranged reads.

Risks: parallel mode requires known object size; the constructor guards this. `maxChunkSize` is irrelevant to parallel mode, which uses fixed rounded chunks in `parallel.go`.

Test signals: `chunkedreader_test.go` checks implementation selection for chunk sizes, stream counts, and unknown size.
