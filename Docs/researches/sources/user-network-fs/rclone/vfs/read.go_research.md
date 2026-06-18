<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read.go -->
# sources/user-network-fs/rclone/vfs/read.go

## Purpose
Implements `ReadFileHandle`, the non-cache read-only handle for VFS files. It wraps backend objects with chunked reading, accounting, optional async buffering, seek/read-at behavior, sequential-read coordination, and optional checksum validation.

## Important APIs, Types, and Functions
Key APIs are `ReadFileHandle`, `newReadFileHandle`, `openPending`, `Seek`, `ReadAt`, `readAt`, `waitSequential`, `checkHash`, `Read`, `Close`, `Flush`, `Release`, `Name`, `Size`, and `Stat`.

## Control Flow
The handle is lazily opened by `openPending`, creating a `chunkedreader` using VFS chunk options and an accounting transfer. `Read` delegates to `readAt` at `roffset`; `ReadAt` calls `readAt` without changing `roffset`. `readAt` optionally waits for nearby in-sequence reads, seeks by range-seek or reopen, retries low-level failures, reads with `io.ReadFull`, handles unknown sizes at EOF, updates offsets, and writes to the hasher. Close closes the accounting reader and validates hashes if a full sequential read occurred.

## State and Persistence Behavior
No writes to the remote. In-memory state tracks object size, whether size is unknown, read and backend offsets, whether opened/closed, no-seek mode, and checksum state. Accounting transfer state is started on open and completed on close.

## Dependencies and Integration Points
Depends on `chunkedreader`, `accounting`, `hash`, global config `LowLevelRetries`, VFS options `NoChecksum`, `NoSeek`, `ReadWait`, `ChunkSize`, `ChunkSizeLimit`, and `ChunkStreams`, and the owning `File`.

## Risks and Edge Cases
`openPending` assumes `fh.file.getObject()` is non-nil. `readAt` checks closed only after opening, so a closed unopened handle may attempt open before returning `ECLOSED`. Hash checking is skipped if seeking invalidates the hasher, if reads did not reach file size, or if source hash is unavailable. Unknown-size reads update size only after EOF. Sequential read waiting launches a goroutine per wait and uses a short timeout to avoid blocking all seeks.

## Test Signals
`read_test.go` covers string/node/size/stat, sequential reads, EOF, seeking, read-at forward/backward/off-end, no-seek errors, close idempotency, flush, and release. `file_test.go` covers unknown-size object reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/read.go -->
