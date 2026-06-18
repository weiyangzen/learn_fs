# sources/storage-engines/foundationdb/flow/include/flow/WatchFile.h

## Purpose
Provides an actor helper that polls a file's last-write time and triggers an `AsyncTrigger` when the file changes or recovers after a stat error.

## Important APIs, Types, And Functions
`watchFileForChanges(filename, fileChanged, intervalSeconds, errorType)` uses `IAsyncFileSystem::lastWriteTime`, `TraceEvent`, `delay`, and `AsyncTrigger`.

## Control Flow
Empty filenames wait forever. Non-empty filenames are statted repeatedly. The first stat establishes baseline time; later timestamp changes or prior stat errors trigger `fileChanged`. `io_error` logs a warning and continues; other errors propagate.

## State And Persistence Behavior
Maintains only `firstRun`, `statError`, and `lastModTime` in memory. It observes metadata only and persists nothing.

## Dependencies And Integration Points
Depends on `IAsyncFile.h` and `genericactors.actor.h`. Used for config/certificate reload style watchers.

## Risks And Edge Cases
Raw pointers must outlive the actor. Timestamp granularity can miss rapid writes. Missing files, permission errors, and symlink loops may all appear as `io_error`.

## Test Signals
Initial stat, modification trigger, missing/inaccessible file warning, recovery trigger, empty filename behavior, and cancellation.
