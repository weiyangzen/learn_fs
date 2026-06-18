# sources/test-tools/fio/engines/sync.c

## Purpose
`sync.c` implements fio's synchronous POSIX file I/O engines: `sync`, `psync`, `vsync`, and conditionally `pvsync`/`pvsync2`. It covers sequential `read`/`write` with `lseek`, positioned `pread`/`pwrite`, vectorized `readv`/`writev`, and newer `preadv2`/`pwritev2` flags.

## Important APIs, Types, And Functions
`struct syncio_data` stores vector I/O arrays, queued `io_u`s, queued byte count, last offset/file/direction for coalescing, and a random state for probabilistic `RWF_HIPRI`. `fio_syncio_prep()` manages `lseek` for the `sync` engine using `fio_file->engine_pos`. `fio_io_end()` centralizes residual/error handling and last-position update. Queue functions implement `pvsync`, `pvsync2`, `psync`, and `sync`. The `vsync` path uses `fio_vsyncio_queue()`, `fio_vsyncio_commit()`, `getevents()`, and `event()` to batch contiguous operations into one vector call.

## Control Flow
Simple engines complete inside `.queue`: they perform read/write/TRIM/sync directly and return `FIO_Q_COMPLETED`. `sync` calls `.prep` first to seek if the requested offset differs from the cached file position. `vsync` queues only adjacent same-file/same-direction requests; non-appendable requests return `FIO_Q_BUSY` so fio commits the current vector and retries. `fio_vsyncio_commit()` marks submissions, seeks to the first offset, calls `readv` or `writev`, stores a completion count, clears the queue, and distributes residuals/errors across queued `io_u`s.

## State And Persistence
State is per-thread. File data persists through normal file descriptors. `fio_file->engine_pos` caches current position for the `sync` engine. `pvsync2` can set `RWF_HIPRI`, `RWF_DONTCACHE`, `RWF_NOWAIT`, and `RWF_ATOMIC` when supported/configured.

## Dependencies And Integration Points
The file uses POSIX `read`, `write`, `pread`, `pwrite`, `readv`, `writev`, optional `preadv2`/`pwritev2`, fio generic file helpers, trim/sync helpers, and fio ioengine registration. `FIO_SYNCFS` indicates syncfs integration, and `pvsync2` advertises `FIO_ATOMICWRITES`.

## Risks
`fio_vsyncio_init()` does not check allocation failures for `sd`, `iovecs`, or `io_us`. `fio_vsyncio_end()` casts remaining byte counts through unsigned `this_io`, so unusual partial/error returns should be reviewed carefully. `RWF_NOWAIT` and `RWF_DONTCACHE` behavior depends on kernel/filesystem support and may produce expected transient errors. Vector batching only works for exact adjacency, file, and direction matches.

## Test Signals
Tests should cover each registered engine, partial read/write residuals, seek caching, TRIM and sync direction delegation, vector coalescing and busy retry, pwritev2 flag combinations, `RWF_ATOMIC` when `oatomic` is set, and conditional build paths for `CONFIG_PWRITEV` and `FIO_HAVE_PWRITEV2`.
