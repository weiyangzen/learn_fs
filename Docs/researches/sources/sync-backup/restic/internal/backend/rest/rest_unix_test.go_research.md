<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go

## Purpose
Tests REST backend behavior over Unix-domain HTTP transport when supported.

## Important APIs, Types, And Functions
The file contains Unix-specific integration tests for http+unix repository URLs.

## Control Flow
It starts or connects to a REST server over a Unix socket and runs backend behavior through the normal REST client stack.

## State And Persistence Behavior
Uses temporary Unix socket/filesystem state.

## Dependencies And Integration Points
Depends on REST integration helpers, unix-capable transport support, and build tags/platform support.

## Risks And Edge Cases
Socket path length and platform support are the main risks; test is platform-specific.

## Test Signals
Covers unixtransport integration configured in http_transport.go.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_unix_test.go -->
