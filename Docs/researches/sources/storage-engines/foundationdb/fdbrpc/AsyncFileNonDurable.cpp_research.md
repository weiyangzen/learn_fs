# sources/storage-engines/foundationdb/fdbrpc/AsyncFileNonDurable.cpp

## Purpose
`AsyncFileNonDurable.cpp` implements simulation wrappers that make async file behavior process-aware and fault-injectable. It models non-durable disks, shutdown races, machine/process context switching, delete/open serialization, and detachable files for FoundationDB simulation.

## Important APIs, Types, and Functions
Top-level helpers include `waitShutdownSignal`, `sendOnProcess`, and `sendErrorOnProcess`. `AsyncFileDetachable` provides `open`, `doShutdown`, and forwarded `read`, `write`, `truncate`, `sync`, and `size` methods that fail after simulated shutdown. `AsyncFileNonDurable::open` wraps a real `IAsyncFile`, initializes approximate size, waits for ongoing deletion, and returns an `AsyncFileNonDurable`. `read`, `closeFile`, and `removeOpenFile` manage machine/process transitions and cleanup.

## Control Flow
Opening captures the current simulated process and task priority, switches to the machine context, waits for the wrapped file or shutdown, blocks behind `filesBeingDeleted` for the same logical filename, constructs the wrapper, initializes its size through the wrapper path, then switches back to the original process. Reads switch to the machine, invoke `onRead`, and switch back before returning or rethrowing. Closing marks the file as deleting/closing, signals pending sync, waits for outstanding modifications, waits for kill completion if needed, removes machine bookkeeping entries, erases deletion guards, and deletes the wrapper.

## State and Persistence Behavior
The wrapper does not implement durable persistence by itself; it records and mediates simulated state around a wrapped file. Shared state includes `AsyncFileNonDurable::filesBeingDeleted`, machine `openFiles`, `closingFiles`, `deletingOrClosingFiles`, pending modification ranges, kill promises, and open address. Shutdown clears detachable references and turns later file calls into injected `io_error`.

## Dependencies and Integration Points
The code depends on `fdbrpc/AsyncFileNonDurable.h`, simulator machine/process info, Flow coroutines, simulator shutdown signals, `g_simulator`, and `g_network`. It integrates tightly with simulation disk fault behavior, process scheduling, and machine-local open file tracking.

## Risks and Edge Cases
The file depends on correct process/machine switching around every operation; missed switches can run callbacks in the wrong simulated process. Delete/open serialization is keyed by logical filename and can block unrelated reopen paths if cleanup fails. `removeOpenFile` defensively handles stale map entries and renamed files, which shows open-file bookkeeping can diverge during simulated deletes or atomic renames. Errors during open must erase `openFiles` based on either the resolved wrapped filename or actual filename.

## Test Signals
Primary signals are simulation tests that kill processes during file operations, delete or rename files while opens are pending, and exercise non-durable disk faults. There are no direct unit tests here; correctness is inferred from simulation stability and absence of leaked open-file/deletion state.
