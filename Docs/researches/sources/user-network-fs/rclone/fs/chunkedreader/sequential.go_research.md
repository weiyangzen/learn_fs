# sources/user-network-fs/rclone/fs/chunkedreader/sequential.go

Purpose: implements a single-stream chunked reader for `fs.Object`, supporting optional range chunking, chunk-size growth, `RangeSeek`, and reuse of range-seekable open readers.

Important APIs/types/functions: `sequential` stores context, source object, current `io.ReadCloser`, next read offset, current chunk start/size, initial and max chunk sizes, custom range-size flag, and closed state. Methods include `newSequential`, `Read`, `Close`, `Seek`, `RangeSeek`, `Open`, `openRange`, and `resetReader`.

Control flow: `Read` locks, rejects closed readers, opens on first read or after seeking, reads up to current chunk boundary with `io.ReadFull`, advances offset, converts `io.ErrUnexpectedEOF` to `io.EOF`, and when a chunk is fully read doubles chunk size up to max unless the last size came from `RangeSeek`, in which case it resets to initial. `RangeSeek` computes the new chunk offset relative to start/current/end, validates object size where needed, sets the next chunk size to the requested length or initial size, and defers reopening until read. `openRange` first tries `RangeSeek` on the existing reader; if that fails it opens the object with `HashesOption{None}` and an optional `RangeOption`.

State and persistence behavior: runtime state is mutex-protected. `offset == -1` means reopen on next read. `chunkSize == -1` means read to end. Closing resets/cleoses the current reader and makes subsequent operations return `ErrorFileClosed`.

Dependencies and integration points: depends on `fs.Object`, `fs.RangeSeeker`, `fs.RangeOption`, `fs.HashesOption`, and hash suppression. It is chosen for unknown-size objects, single-stream mode, or disabled parallelism.

Risks: validation rejects `chunkOffset >= size`, so seeking exactly to EOF is invalid. When object size is unknown, seeking from end is invalid. Reusing an existing `RangeSeeker` is an optimization but falls back to reopening if the returned offset or error is unsuitable.

Test signals: shared tests and `sequential_test.go` cover read correctness across chunk sizes, source seek modes, and closed-reader errors.
