<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_internal_test.go -->
# sources/sync-backup/restic/internal/backend/local/local_internal_test.go

## Purpose
Tests local backend internal cleanup/error behavior around failed temp file saves.

## Important APIs, Types, And Functions
The tests override tempFile and exercise Save failure paths.

## Control Flow
Control flow creates a local backend, injects temp-file behavior, triggers Save errors, and asserts cleanup expectations.

## State And Persistence Behavior
Uses temporary filesystem state and restores package-level tempFile after testing.

## Dependencies And Integration Points
Depends on local package internals, backend.NewByteReader, context, and internal/test helpers.

## Risks And Edge Cases
Because it mutates a package variable, test isolation depends on restoring tempFile correctly.

## Test Signals
Provides regression coverage for partial-file cleanup paths that normal suite tests rarely hit.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/local_internal_test.go -->
