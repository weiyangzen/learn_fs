<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/semaphore.go -->
# sources/sync-backup/restic/internal/backend/sema/semaphore.go

## Purpose
Implements the small counting semaphore used by the connection-limited backend.

## Important APIs, Types, And Functions
semaphore type, newSemaphore, GetToken, and ReleaseToken are relevant.

## Control Flow
newSemaphore creates a buffered channel with capacity n and rejects zero. GetToken sends into the channel; ReleaseToken receives.

## State And Persistence Behavior
State is channel occupancy only.

## Dependencies And Integration Points
Depends on internal/errors for invalid count reporting.

## Risks And Edge Cases
Mispaired acquire/release can deadlock or panic; callers use defer to pair operations.

## Test Signals
Covered indirectly by sema backend tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sema/semaphore.go -->
