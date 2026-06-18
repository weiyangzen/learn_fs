<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend.go -->
# sources/sync-backup/restic/internal/backend/sema/backend.go

## Purpose
Wraps a backend with connection-count limiting, parameter validation, and freeze/unfreeze coordination.

## Important APIs, Types, And Functions
NewBackend, connectionLimitedBackend, typeDependentLimit, Freeze, Unfreeze, Save, Load, Stat, Remove, and Unwrap are the API.

## Control Flow
Each operation validates handles/offset/length, skips limits for lock files, acquires a semaphore token, respects freezeLock, checks context cancellation, then delegates. Freeze blocks new non-lock operations after token acquisition.

## State And Persistence Behavior
State is semaphore tokens, freezeLock, and wrapped backend; persistence is delegated.

## Dependencies And Integration Points
Depends on context, io, sync, backoff, internal/backend/errors.

## Risks And Edge Cases
Lock-file bypass is intentional to keep lock refresh possible. Panic on invalid backend connection count happens during NewBackend.

## Test Signals
backend_test.go covers validation, concurrency limits, lock bypass, freeze behavior, and Unwrap.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/backend.go -->
