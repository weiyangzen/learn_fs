# sources/test-tools/fio/engines/libblkio.c

## Purpose
Implements a fio engine backed by libblkio, allowing fio workloads to target libblkio drivers and queue APIs rather than conventional file descriptors. It supports normal and poll queues, vectored read/write, discard or write-zeroes trim, custom libblkio properties, eventfd or polling completion waits, and libblkio-managed memory regions.

## Important APIs, Types, And Functions
Process-wide `proc_state` holds a mutex, initialized-thread counts, hipri-thread counts, and one shared `struct blkio *`. Per-thread `struct fio_blkio_data` stores a `struct blkioq *`, optional completion fd, optional allocated memory region, iovecs, and completion slots. `struct fio_blkio_options` contains driver/path/property strings, queue sizing, `hipri`, `vectored`, trim behavior, wait mode, and completion-eventfd forcing.

Key functions are `fio_blkio_set_props_from_str()`, `fio_blkio_check_opt_compat()`, `fio_blkio_create_and_connect()`, `fio_blkio_setup()`, `fio_blkio_init()`, `fio_blkio_post_init()`, `fio_blkio_iomem_alloc()`, `fio_blkio_iomem_free()`, `fio_blkio_queue()`, `fio_blkio_getevents()`, and `fio_blkio_event()`.

## Control Flow
`setup` validates threaded-subjob option compatibility, rejects incompatible hipri/eventfd combinations, creates a temporary blkio instance to fetch capacity, and records file size. `init` creates or reuses the process-wide blkio instance under a mutex, configures queue counts, starts libblkio, assigns each fio thread a regular or poll queue, optionally enables a blocking completion eventfd, and stores per-thread data. `post_init` maps fio core buffers into libblkio unless libblkio allocated them. `queue` calls the corresponding `blkioq_*` operation and attaches `io_u` as user data. `getevents` waits with blocking `blkioq_do_io()`, eventfd-driven polling, or busy-loop polling, and `event` maps completions back to `io_u` while translating `completion->ret`.

## State And Persistence
State is split between one shared libblkio object per process and per-thread queues. Memory regions may be owned by fio or allocated/mapped by libblkio. Persistent data effects are delegated to the selected libblkio driver; fio itself marks the engine diskless and no-extend because capacity and file I/O semantics are external.

## Dependencies And Integration Points
Depends on libblkio, fio options parsing helpers, fio threading model, memory allocation hooks, and `ioengine_ops` setup/init/post-init phases. The engine must coordinate with fio's `thread` option because multiple jobs in one process share the same libblkio object.

## Risks
Shared process state is subtle: incompatible threaded subjobs are tracked globally and all such jobs fail later. Cleanup destroys the shared blkio only when the last thread exits. Eventfd mode changes file descriptor blocking state. Memory-region length is recomputed to avoid fio padding that may violate libblkio alignment. The option parser mutates a duplicated property string; malformed `name=value` lists fail setup.

## Test Signals
Test single-process and threaded multi-job workloads, hipri and non-hipri queues, all wait modes, forced eventfd, custom properties before connect/start, vectored and non-vectored read/write, discard vs write-zeroes trim, libblkio-managed memory allocation/free, incompatible threaded option detection, and cleanup when jobs finish at different times.
