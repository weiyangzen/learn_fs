# sources/storage-engines/foundationdb/fdbrpc/AsyncFileKAIO.h

## Purpose
`AsyncFileKAIO.h` implements FoundationDB's Linux-only unbuffered `IAsyncFile` backend using kernel AIO, `eventfd`, and direct I/O. It is selected when POSIX KAIO is enabled and exposes asynchronous read/write, truncate, size, sync, zero-range, file locking, and atomic-create behavior.

## Important APIs, Types, and Functions
The main type is `AsyncFileKAIO`, a final `IAsyncFile`/`ReferenceCounted` implementation. Important entry points are `open`, `init`, `setTimeout`, `read`, `write`, `zeroRange`, `truncate`, `sync`, `size`, `debugFD`, `launch`, and `poll`. Internal types include `IOBlock`, which embeds `linux_iocb` and carries result promises, owner references, priority, timeout-list pointers, and start times, and `Context`, the singleton KAIO context holding `io_context_t`, eventfd, queues, outstanding counts, timeout state, metrics, and fallocate capability flags. `AsyncFileKAIOMetrics` exposes latency samples for reads, writes, and syncs; `SlowAioSubmit` is an event metric payload for slow submissions.

## Control Flow
`open` translates Flow open flags to `O_DIRECT | O_CLOEXEC` POSIX flags, optionally uses `filename + ".part"` for atomic create, applies advisory mandatory-lock setup, records initial file size, and returns the file object. `init` calls `io_setup`, stores the eventfd, starts the `poll` actor, and registers `launch` as the network run-cycle hook. Reads and writes allocate an `IOBlock`, set buffer/length/offset, enqueue it by task priority, and return the block promise. `launch` drains queued blocks up to `MAX_OUTSTANDING`, extends files before submit when `nextFileSize` exceeds `lastFileSize`, calls `io_submit`, increments outstanding counts, and requeues unsubmitted requests. `poll` waits on eventfd, collects completions with `io_getevents`, handles timeout scanning, records latency, and delivers promises at the original task priority.

## State and Persistence Behavior
Persistent state is the underlying file descriptor plus tracked logical file size (`lastFileSize`/`nextFileSize`) and open flags. Durability depends on `sync`, which uses `AsyncFileEIO::async_fdatasync`; if `OPEN_ATOMIC_WRITE_AND_CREATE` is set, the `.part` file is atomically renamed after the sync future completes. The global `Context` owns all KAIO queueing and timeout state for the process. A timeout marks the file failed unless configured warn-only, causing later operations to fail with `io_timeout`.

## Dependencies and Integration Points
The file depends on Linux KAIO wrappers (`linux_kaio.h`), `eventfd`, POSIX file APIs, Flow futures/actors, knobs, metrics, CRC32C for optional logging, and `AsyncFileEIO` for fdatasync/rename fallback. It integrates with `IAsyncFileSystem`, Flow network global run-cycle hooks, task priorities, network disk-stall metrics, and trace/event metrics.

## Risks and Edge Cases
All enqueued buffers, offsets, and lengths must be 4096-byte aligned; violations assert. `zeroRange` checks `fallocate` incorrectly against `EOPNOTSUPP` as a direct return code rather than via `errno`, so unsupported zeroing can be misdetected. Pre-submit file extension synchronously calls `truncate`/`fallocate` inside `launch`, which can stall the network loop and is monitored as slow submit. Partial `io_submit` handling assumes non-EAGAIN errors correspond to the first I/O. Timeout handling marks file-level failure but cannot cancel already submitted KAIO requests. `KAIO_LOGGING` writes to a hardcoded path and should remain disabled outside investigations.

## Test Signals
Signals are mostly integration-level: direct-I/O file tests, storage engine simulation tests using unbuffered files, latency/slow-submit events, timeout fault-injection behavior, and atomic-create rename correctness. There is no focused unit test in this subset for KAIO queue ordering, timeout list removal, or fallocate fallback.
