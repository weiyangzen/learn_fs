<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_int_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_int_test.go

## Purpose
Integration-tests the REST backend against an external rest-server binary.

## Important APIs, Types, And Functions
runRESTServer and backend suite tests are the main logic.

## Control Flow
The helper starts rest-server, parses stderr for the listen address, runs shared backend tests/benchmarks, and cleans up via process cancellation/kill fallback.

## State And Persistence Behavior
Uses temporary directories, external process state, and HTTP network sockets.

## Dependencies And Integration Points
Depends on os/exec, net/url, regexp, syscall, backend/test Suite, and rest config.

## Risks And Edge Cases
Skipped when rest-server is unavailable; startup log parsing and process cleanup are platform-sensitive.

## Test Signals
Provides high-value integration coverage against the actual REST server protocol.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_int_test.go -->
