<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/layout_test.go -->
# sources/sync-backup/restic/internal/backend/local/layout_test.go

## Purpose
Validates that a fixture repository using the default layout can be opened by the local backend and lists expected pack files.

## Important APIs, Types, And Functions
TestLayout is the only test.

## Control Flow
The test extracts a tar fixture, opens the repo, lists PackFile handles, verifies expected IDs and no unexpected IDs, then closes and removes the repo.

## State And Persistence Behavior
Uses temporary filesystem state from test fixtures.

## Dependencies And Integration Points
Depends on local.Open, backend.PackFile, filepath, context, and internal/test fixture helpers.

## Risks And Edge Cases
Coverage is fixture-based and skips alternate layouts; failures often indicate path mapping or List regression.

## Test Signals
Strong integration signal for local layout compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/layout_test.go -->
