<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_test.go -->
# sources/sync-backup/restic/internal/backend/rest/rest_test.go

## Purpose
Unit-tests REST List behavior for API v1 and v2 response formats.

## Important APIs, Types, And Functions
TestListAPI is the key test.

## Control Flow
An httptest server returns JSON list data. v1 cases require subsequent HEAD requests for sizes; v2 includes sizes in one request. The test asserts returned FileInfo slices and request counts.

## State And Persistence Behavior
No persisted state beyond httptest server counters.

## Dependencies And Integration Points
Depends on net/http/httptest, backend/rest, reflect, strconv.

## Risks And Edge Cases
Does not exercise Save/Load; focused on list parsing and protocol negotiation.

## Test Signals
Strong regression signal for REST listing efficiency and compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/rest_test.go -->
