# sources/user-network-fs/rclone/fs/chunkedreader/parallel.go

Purpose: implements multi-stream chunked reading of known-size `fs.Object` values by opening ranged streams in parallel and serving them in order.

Important APIs/types/functions: `parallel` tracks source object, current offset, end offset with launched streams, rounded chunk size, target stream count, active `stream` slice, and closed state. `stream` wraps one ranged download, its cancelable context, `io.ReadCloser`, offset/size, bytes served, `pool.RW` buffer, error channel, and debug name. Methods include `newStream`, `stream.readFrom`, `stream.eof`, `stream.read`, `stream.close`, `newParallel`, `_open`, `_popStream`, `_popStreams`, `Read`, `Close`, `Seek`, `RangeSeek`, and `Open`.

Control flow: `newParallel` rounds chunk size up to a multiple of `multipart.BufferSize` and defaults negative sizes to that buffer size. `_open` launches enough streams to reach `nstreams`, clipping the final chunk to object size. Each stream goroutine opens the object with `operations.Open` and a `RangeOption`, then pipes the response into a multipart RW buffer. `Read` holds the reader mutex, ensures streams are open, reads from the first stream, advances global offset, closes completed streams, and continues until the caller buffer is full or an error/EOF occurs. `Seek` computes the new absolute offset, rejects out-of-range seeks, drops completed/out-of-range streams, seeks within the current buffered stream when possible, or restarts stream scheduling from the new offset.

State and persistence behavior: runtime-only state is guarded by `mu`. Stream goroutines are canceled and drained during `_popStream`/`Close`. `endStream` records how far prefetch has been scheduled so new streams continue after retained streams. `RangeSeek` ignores the length argument and delegates to `Seek`.

Dependencies and integration points: depends on `fs.Object`, `operations.Open`, `hash.None`, `RangeOption`, `multipart.NewRW`, `pool.RW`, logging, and standard `io`. It is selected by `New` when streams > 1 and object size is known.

Risks: concurrency and cancellation are the main risks. `stream.close` waits on the goroutine error channel, so `readFrom` must always send exactly one error. `Seek` waits for buffered data to reach the seek target within a stream, which can block if the stream stalls or context is canceled. `RangeSeek` length is ignored in parallel mode, which is intentional but different from sequential mode. The code rejects seeking exactly to `size`, so callers cannot seek to EOF.

Test signals: `parallel_test.go` exercises multi-mode reads, close errors, large sequential reads, rewinds, end-relative seeks, and randomized backward seeks.
