# sources/storage-engines/pebble/internal/cache/cache.go

Purpose: Implements the public surface of Pebble's sharded block cache and cache handles, backed by per-shard CLOCK-Pro replacement and manual-memory values.

APIs and types: `Cache`, `New`, `NewWithShards`, `Ref`, `Unref`, `NewHandle`, `Reserve`, `MaxSize`, `Size`, `Handle`, `handleID`, `Handle.Cache`, `Peek`, `Get`, `GetWithReadHandle`, `Set`, `Delete`, `EvictFile`, `Close`, and `CategoryHidden`.

Control flow and state: `New` chooses shard count as `4*GOMAXPROCS` unless that would create tiny shards, then initializes shards and metrics windows. Cache lifetime is reference-counted; `Unref` destroys shards at zero. Handles allocate unique namespace IDs and keep cache refs. Gets route a `(handleID,fileNum,offset)` key to a shard; `GetWithReadHandle` coordinates cache misses with read-entry turn taking and context cancellation. `Reserve` temporarily lowers effective shard capacity and returns a one-shot release closure.

Persistence and dependencies: Cache contents are runtime-only copies of immutable table blocks. Depends on base file/level types, shard/read-entry/value implementations, metrics windows, atomics, sync, runtime/debug, invariants, and errors.

Integration points: Used by DB/table readers to share blocks across Pebble instances while isolating file-number namespaces by handle. Exposes metrics and read-handle coordination for block reads.

Risks: Every `Value` returned by get paths must be released by callers. Cache and handle refs must be balanced or invariant finalizers exit. Manual memory leaks or double releases are serious. `Reserve` closure panics on double release. Read-handle callers must call `SetReadValue` or `SetReadError` when they receive a valid handle.

Test signals: This subset includes `block_map_test.go`; broader cache behavior is tested in other cache package tests such as clockpro/read-shard/value tests not assigned here.
