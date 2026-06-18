<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go -->
# sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go

## Purpose

`asyncreader.go` implements an asynchronous read-ahead `io.ReadCloser` used to buffer object reads independently from consumers.

## Important APIs, Types, and Functions

Exports are `BufferSize`, `ErrorStreamAbandoned`, `AsyncReader`, and `New`. Methods include `Read`, `WriteTo`, `SkipBytes`, `StopBuffering`, `Abandon`, and `Close`. Internal `buffer` objects hold pooled byte slices, terminal errors, and offsets.

## Control Flow

`New` validates input, initializes buffered channels and tokens, then starts a goroutine. The goroutine consumes tokens, gets pool buffers, soft-starts buffer size from 4 KiB up to `pool.BufferSize`, fills buffers with `readers.ReadFill`, sends them on `ready`, and exits on error or stop. Consumers call `fill`, serve data, return exhausted buffers, and propagate stored errors after buffered bytes are consumed.

## State and Persistence Behavior

State is per-reader memory: input stream, ready/token channels, current buffer, error, shutdown channels, pool reference, and closed flag. No data is persisted, but buffers are borrowed from a global pool and must be returned through `Abandon`/`Close`.

## Dependencies and Integration Points

It integrates with accounting buffering, `lib/pool`, `lib/readers`, `fs.ConfigInfo`, and any code that benefits from `io.WriterTo` acceleration or limited forward seeking with `SkipBytes`.

## Risks and Test Signals

Risks include deadlocks when stopping during reads, buffer leaks on abandon/error paths, `SkipBytes` token accounting mistakes, duplicate close behavior, and returning `ErrorStreamAbandoned` versus stored EOF/error correctly. Tests should cover short reads, EOF after buffered bytes, `WriteTo`, backward/forward skips, abandon/close races, and pool return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go -->
