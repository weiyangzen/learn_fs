# sources/storage-engines/pebble/objstorage/objstorageprovider/readahead_test.go

Purpose: This file provides data-driven coverage for the dynamic readahead state machine in `readahead.go`. It validates both normal reads and cache-hit notifications against expected internal state snapshots.

Important functions: `TestMaybeReadahead` initializes `readaheadState` with a 256 KiB max and processes commands from `testdata/readahead`. Supported commands are `reset`, `read`, and `cache-read`. Each read parses `offset,size`, calls either `maybeReadahead` or `recordCacheHit`, and prints `readahead`, `numReads`, `size`, `prevSize`, and `limit`.

Control flow and state: The test exposes otherwise-private state, making it a white-box behavioral contract. `reset` preserves `maxReadaheadSize` while returning the state to initial conditions. `cache-read` verifies that cache hits affect sequentiality and `limit` without producing a prefetch size.

Dependencies and integration: The test uses `datadriven`, `require`, and string parsing only; it does not perform actual file or remote reads. This isolates the state machine from VFS or remote object storage behavior.

Risks and test signals: Because output includes every mutable field, the fixture catches changes in exponential growth, thresholding, random-read reset behavior, and cache-hit handling. It does not directly validate integration with `vfs.File.Prefetch` or remote buffers; those paths are exercised by provider and remote read-handle tests.
