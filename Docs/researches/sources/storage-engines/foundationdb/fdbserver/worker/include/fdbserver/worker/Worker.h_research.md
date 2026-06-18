# sources/storage-engines/foundationdb/fdbserver/worker/include/fdbserver/worker/Worker.h

## Purpose
`Worker.h` declares the top-level worker process entry point and profiling registration hook for fdbserver worker code.

## Important APIs, Types, And Functions
`Future<Void> fdbd(...)` is the main worker actor entry point. It receives the cluster connection record, locality, process class, data/tlog/coord folders, memory limit, metrics connection/prefix, memory profiling threshold, binary whitelist paths, and consistency-check urgent-mode flag. `registerThreadForProfiling()` registers the current thread with profiling infrastructure.

## Control Flow
The header only declares functions. The implementation is responsible for launching worker roles, metrics, coordination, storage, TLog spill folders, and consistency-check behavior.

## State And Persistence Behavior
The function signature exposes persistent and runtime configuration: data folder, TLog spill folder, coordination folder, metrics database information, and memory limits. No state is defined in the header.

## Dependencies And Integration Points
It depends on client cluster connection records, coordination interface, FDB types, locality data, process class, and Flow futures. It is the public include used by process startup.

## Risks And Test Signals
Because `fdbd` is broad and process-level, signature changes have high integration cost. Tests are likely indirect through worker startup/link tests rather than this header itself.
