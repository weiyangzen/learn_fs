<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend.go -->
# sources/sync-backup/restic/internal/backend/mem/mem_backend.go

## Purpose
Implements an in-memory backend for tests and ephemeral repositories.

## Important APIs, Types, And Functions
MemoryBackend, NewFactory, New, Save, Load/openReader, Stat, Remove, List, Properties, Hasher, Delete, Close, Warmup/WarmupWait, and error helpers are important.

## Control Flow
Save normalizes metadata/config handles, rejects overwrite, reads all bytes, verifies length and xxhash content hash, then stores bytes in a mutex-protected map. Load/Stat/Remove/List copy map metadata under lock and honor context errors.

## State And Persistence Behavior
All repository state is held in a map[backend.Handle][]byte. NewFactory intentionally returns a persistent singleton for create/open calls.

## Dependencies And Integration Points
Depends on sync, bytes, xxhash, backend/location/util, debug/errors.

## Risks And Edge Cases
Because state is process-local, it is not durable and can grow unbounded in tests. Hash verification assumes RewindReader.Hash matches Hasher output.

## Test Signals
mem_backend_test.go runs the generic backend suite and benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mem/mem_backend.go -->
