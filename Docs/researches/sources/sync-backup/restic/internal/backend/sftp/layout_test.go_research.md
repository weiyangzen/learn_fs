<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/layout_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/layout_test.go

## Purpose
Verifies SFTP can open a fixture repository using the default layout and list expected pack files.

## Important APIs, Types, And Functions
TestLayout is the only test.

## Control Flow
The test extracts a fixture, starts an sftp-server command, opens the repo, lists pack files, checks expected IDs, closes, and removes temp data.

## State And Persistence Behavior
Uses temporary filesystem state and external sftp-server process.

## Dependencies And Integration Points
Depends on sftp.Open, backend.PackFile, context, filepath, and internal/test fixtures.

## Risks And Edge Cases
Skipped when sftp-server is unavailable; process startup can be environment-sensitive.

## Test Signals
Integration signal for SFTP layout compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/layout_test.go -->
