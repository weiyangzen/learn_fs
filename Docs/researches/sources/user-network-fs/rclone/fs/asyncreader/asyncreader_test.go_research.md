# sources/user-network-fs/rclone/fs/asyncreader/asyncreader_test.go

Purpose: exercises the asynchronous read-ahead reader implementation in `fs/asyncreader`, especially EOF propagation, `io.WriterTo`, abandoned streams, and bounded skipping across prefetched buffers. The tests are implementation-aware: they reference `New`, `AsyncReader.Read`, `WriteTo`, `Close`, `Abandon`, `SkipBytes`, `BufferSize`, `softStartInitial`, and `ErrorStreamAbandoned`.

Important APIs and helpers: `TestAsyncReader` validates simple read/EOF behavior, repeated EOF after the terminal error, idempotent close, and closing before draining a large stream. `TestAsyncWriteTo` verifies the `io.Copy`/`WriteTo` path returns bytes once and no error on a second copy after EOF. `TestAsyncReaderErrors` covers nil reader and invalid buffer counts. `readMaker`, `bufReader`, `reads`, `bufsizes`, and the size/write tests borrow bufio-style cases to vary upstream reader behavior, downstream read sizes, internal `bufio.Reader` sizes, and async buffer counts. `zeroReader` and `testAsyncReaderClose` model an infinite source so `Abandon` can interrupt both `Read` loops and `WriteTo`. `TestAsyncReaderSkipBytes` uses deterministic random data and many initial-read/skip combinations to check successful in-buffer forward/backward skipping and failure paths.

Control flow: most tests construct `AsyncReader` with `context.Background()` and an `io.NopCloser` source, then drive either `Read`, `io.Copy`, direct `WriteTo`, or `readers.ReadFill`. The skip test reads an initial prefix, calls `SkipBytes`, then reads 1024 bytes and compares the result with the expected offset when the skip succeeds. When the skip is impossible, it expects either EOF or `ErrorStreamAbandoned` because `SkipBytes` abandons the reader on failure.

State and persistence: the tests are in-memory only, but they assert important lifecycle state: EOF is sticky once observed, `Close` closes underlying resources without double-close panics, and `Abandon` unblocks concurrent readers. The `zeroReader.closed` flag is a guard against double-closing the input.

Dependencies and integration points: depends on `testing/iotest` reader wrappers, `bufio`, `readers.ReadFill`, `israce.Enabled`, and the async reader implementation. The race detector skip avoids a known Go runtime race-related issue for multi-buffer cases.

Risks: async reader correctness is concurrency-sensitive. The tests cover many data paths but do not inspect internal goroutine cleanup directly beyond unblocking and close behavior. `TimeoutReader` is intentionally treated as non-recovering for async reads, so it documents a behavioral difference from some synchronous reader expectations.

Test signals: strong coverage for EOF semantics, `WriterTo`, abandoning, invalid constructor input, buffer sizing, read sizes, and skip boundaries. The test matrix gives high confidence in byte-for-byte delivery across read-ahead boundaries.
