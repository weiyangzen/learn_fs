# sources/storage-engines/wiredtiger/src/include/os_fhandle_inline.h

## Purpose
Defines inline wrappers around `WT_FILE_HANDLE` operations, adding WiredTiger assertions, verbose tracing, statistics, latency histograms, corruption flags, panic checks, and write accounting.

## Important APIs, Types, And Functions
- `__wt_fsync` dispatches to blocking or nonblocking sync operations and updates fsync stats.
- `__wt_fextend` extends files through `fh_extend_nolock` or `fh_extend`.
- `__wt_file_lock` wraps file locking.
- `__wt_read` dispatches `fh_read`, tracks active readers/read I/O, records latency, and flags data corruption on read failure.
- `__wt_filesize` wraps `fh_size`.
- `__wt_ftruncate` wraps `fh_truncate` with readonly and diagnostic backup assertions.
- `__wt_write` checks readonly/panic state, dispatches `fh_write`, records latency/stats, and increments `fh->written`.

## Control Flow
Each wrapper logs the operation, fetches the vtable from `fh->handle`, and calls the configured method if available. Unsupported extend/truncate operations return `ENOTSUP` through WiredTiger error handling. Read/write paths bracket vtable calls with active-thread counters and clock measurements. Write performs a panic check immediately before I/O to avoid continuing writes after a fatal state.

## State And Persistence Behavior
These functions perform durable file operations through the filesystem extension layer. They mutate runtime counters and `fh->written`; sync/truncate/extend/write change persistent file state. Diagnostic backup checks prevent shrinking files during backup.

## Dependencies And Integration Points
Depends on `WT_FH`, `WT_FILE_HANDLE` vtables, connection readonly/in-memory flags, stats/histograms, verbose logging, panic checks, backup state, atomic counters, and filesystem extension implementations. Integrated with block manager, logging, metadata, checkpoint, and backup code.

## Risks
Vtable methods may be null; callers must handle `ENOTSUP`. Read failure sets a connection data-corruption flag, which can affect startup/error handling. `__wt_write` allows readonly writes only for the single-thread lock file path. Diagnostic backup assertions depend on accurate file size methods.

## Test Signals
Filesystem tests should inject vtable success/failure/null methods, verify stat and histogram updates, check readonly enforcement, validate panic-before-write behavior, assert data-corruption flag on read error, and cover backup shrink assertions under diagnostic builds.
