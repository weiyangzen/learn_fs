<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/display_location_test.go -->
# sources/sync-backup/restic/internal/backend/location/display_location_test.go

## Purpose
Tests password stripping through the public registry/factory path rather than only package-local functions.

## Important APIs, Types, And Functions
TestStripPassword is the primary test.

## Control Flow
The test registers backend factories and checks displayed locations no longer include secrets.

## State And Persistence Behavior
No persisted state beyond an in-memory registry.

## Dependencies And Integration Points
Depends on location package, backend factories, and testing.

## Risks And Edge Cases
Coverage focuses on masking behavior and protects logging/display paths from leaking credentials.

## Test Signals
Complements location and backend-specific StripPassword tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/display_location_test.go -->
