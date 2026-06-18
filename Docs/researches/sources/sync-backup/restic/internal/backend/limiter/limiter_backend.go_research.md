<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go -->
# sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go

## Purpose
Wraps a backend so Save uploads and Load downloads are rate-limited through a Limiter.

## Important APIs, Types, And Functions
WrapBackendConstructor, LimitBackend, rateLimitedBackend.Save/Load/Unwrap, limitedRewindReader, limitedReader, and newDownstreamLimitedReader are the key pieces.

## Control Flow
Save replaces the RewindReader Read path with limiter.Upstream while preserving Rewind/Length/Hash. Load wraps the callback reader in limiter.Downstream and preserves WriterTo by routing writes through DownstreamWriter.

## State And Persistence Behavior
No persistence; it decorates an existing backend and carries a Limiter reference.

## Dependencies And Integration Points
Depends on context/io, internal/backend, and limiter implementations. Integrated through location.NewLimitedBackendFactory and backend construction.

## Risks And Edge Cases
A subtle risk is losing io.WriterTo fast paths or RewindReader metadata; the wrapper explicitly preserves both but only when source reader implements WriterTo.

## Test Signals
TestLimitBackendSave and TestLimitBackendLoad verify byte integrity and WriterTo preservation paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/limiter/limiter_backend.go -->
