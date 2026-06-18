# sources/sync-backup/syncthing/lib/scanner/blockqueue.go

## Purpose
Provides file hashing orchestration: hash one file safely and run multiple hasher goroutines over a queue of `FileInfo` values produced by the filesystem walker.

## Important APIs, Types, and Functions
`HashFile` opens a file, records size and modtime, hashes blocks with `Blocks`, updates hashed-byte metrics, and verifies the file did not change. `parallelHasher`, `newParallelHasher`, `hashFiles`, and `closeWhenDone` implement the worker pool.

## Control Flow
`HashFile` opens the path, stats before hashing, calls `Blocks` with a size limit, stats again, and returns an error if size or modtime changed. `newParallelHasher` starts N workers and a closer goroutine. Each worker reads `FileInfo` from the inbox, rejects directories/deleted files with panic, hashes regular files, fills `Blocks`, computes `BlocksHash`, recomputes size from block sizes, and emits a `ScanResult` unless context is canceled. `closeWhenDone` waits for workers, drains the inbox if needed, signals optional done, and closes the outbox.

## State and Persistence Behavior
No durable state is stored. The code opens and reads filesystem files and updates Prometheus counters. It mutates `FileInfo` values in memory before sending them downstream.

## Dependencies and Integration Points
Depends on the scanner block hashing code, Syncthing filesystem abstraction, protocol `FileInfo`/`BlockInfo`, and scanner error handling. It is invoked by `Walk` after `walkRegular` identifies changed files.

## Risks and Edge Cases
Files modified during hashing are rejected, preventing stale block hashes. Worker count must be positive; zero workers would leave the outbox closing immediately without hashing queued files. Draining the inbox on context abort avoids blocking the walker. Panics protect against internal misuse if directories or deleted files reach hashers.

## Test Signals
`blocks_test.go` covers the lower-level block hashing. Virtual filesystem tests in this subset provide fake files suitable for scanner tests elsewhere. Direct worker-pool tests would check changed-file errors, context cancellation, and channel closure behavior.
