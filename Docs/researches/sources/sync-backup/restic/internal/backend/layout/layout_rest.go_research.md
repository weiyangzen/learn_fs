<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_rest.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_rest.go

## Purpose
Implements REST protocol path layout, where data files are not sharded into two-character subdirectories.

## Important APIs, Types, And Functions
RESTLayout, NewRESTLayout, String, Name, Dirname, Filename, Paths, and Basedir are the API.

## Control Flow
Filename and Dirname join the base URL with type directories; ConfigFile is special-cased to base/config and base directory. Basedir always reports no subdirectories.

## State And Persistence Behavior
Stores only a base URL string. REST server persistence is handled by HTTP requests in the rest backend.

## Dependencies And Integration Points
Depends on path and internal/backend; consumed by internal/backend/rest and rclone via the REST backend.

## Risks And Edge Cases
URL concatenation assumes the supplied base URL has already had trailing slash normalization by rest.Open.

## Test Signals
Covered by layout/layout_test.go and REST backend list/save/load tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_rest.go -->
