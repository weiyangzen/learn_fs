<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mock/backend.go -->
# sources/sync-backup/restic/internal/backend/mock/backend.go

## Purpose
Defines a callback-driven mock backend for unit tests of wrappers and retry/semaphore logic.

## Important APIs, Types, And Functions
Backend struct with function fields, NewBackend, and methods implementing backend.Backend are the API.

## Control Flow
Each method calls its configured function when set, otherwise returns a useful default such as nil Close, default Properties, or not-implemented errors for operations.

## State And Persistence Behavior
No persistence unless a test callback stores state.

## Dependencies And Integration Points
Depends on context, hash, io, internal/backend, and internal/errors.

## Risks And Edge Cases
Tests using it must set function fields needed by the code path; missing functions can hide behavior behind defaults.

## Test Signals
Used heavily by limiter, retry, and sema tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/mock/backend.go -->
