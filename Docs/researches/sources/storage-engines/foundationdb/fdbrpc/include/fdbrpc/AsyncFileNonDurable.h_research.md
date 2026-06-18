# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/AsyncFileNonDurable.h

## Purpose
`AsyncFileNonDurable.h` implements simulation-only async file wrappers that model shutdown, process detachment, delayed writes, non-durable sync, dropped writes, corrupted sectors, dropped truncates, and power-failure behavior.

## Important APIs, Types, and Functions
Helpers include `sendOnProcess`, `sendErrorOnProcess`, `waitShutdownSignal`, and template `sendErrorOnShutdown`. `AsyncFileDetachable` wraps a file that can detach on shutdown. `AsyncFileNonDurable` implements `open`, `read`, `write`, `truncate`, `sync`, `size`, `kill`, `removeOpenFile`, and close handling. Internal actors include `checkKilled`, `onRead`, delayed `write`, delayed `truncate`, `onSync`, `sync`, `onSize`, and `closeFile`.

## Control Flow
Public writes and truncates create promises that are completed once the operation has logically started, while internal actors delay actual underlying I/O according to disk parameters and simulation speed. Pending modification ranges are tracked so reads wait for overlapping writes/truncates. `sync(true)` forces pending operations to finish durably and syncs the wrapped file. `kill()` calls `sync(false)`, signals pending operations to stop delaying, and may write correctly, drop data, corrupt sectors, drop truncates, or sometimes sync depending on randomized kill mode and prior sync state.

## State and Persistence Behavior
The wrapped file holds durable data; `AsyncFileNonDurable` overlays in-memory pending modifications, approximate size, lower-bound size after modifications, killed/killComplete promises, sync trigger promise, disk parameters, `hasBeenSynced`, kill mode, and actor collection. It also has static `filesBeingDeleted` and open-file map interactions.

## Dependencies and Integration Points
It depends on Flow actors, `IAsyncFile`, simulator APIs, `TraceFileIO`, `RangeMap`, disk parameter helpers, knobs, and process switching through `g_simulator`. It integrates into simulation file systems to test storage recovery under non-durable writes.

## Risks and Edge Cases
This code is intentionally fault-injecting, so callers must expect injected `io_error`s and corruption. Pending range tracking must remain consistent with `minSizeAfterPendingModifications`; bugs can allow reads before overlapping writes settle. `delref` starts asynchronous close/delete behavior and must avoid using object fields after kill completion can delete the wrapper. AIO mode asserts page-aligned writes.

## Test Signals
Simulation storage tests that reboot or kill processes are the main signals. Trace events such as `AsyncFileNonDurable_BadWrite`, `DroppedWrite`, `DroppedTruncate`, and debug file checks show injected behavior.
