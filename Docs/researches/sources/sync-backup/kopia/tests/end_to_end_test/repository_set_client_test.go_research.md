# sources/sync-backup/kopia/tests/end_to_end_test/repository_set_client_test.go

## Purpose
Tests mutable client-side repository settings through `repo set-client`.

## Important APIs, Types, and Functions
`formatSpecificTestSuite.TestRepositorySetClient` and helper `verifyHasLine`.

## Control Flow
The test creates a repo with description, username, hostname, and format cache duration; verifies status lines; sets read-only, description, hostname, and disables format cache; verifies status; asserts snapshot create fails in read-only mode; switches back to read-write with a 5s cache duration; snapshots successfully and verifies status.

## State and Persistence Behavior
Mutates local client config rather than repository data for read-only/description/host/cache settings. Snapshot after read-write creates repository content.

## Dependencies and Integration Points
Exercises repo create flags, repo status output, client config mutation, read-only enforcement in snapshot create, and cache duration formatting.

## Risks
Status text matching is substring-based but still coupled to labels and duration formatting. It does not inspect config files directly.

## Test Signals
Confirms set-client changes are reflected in status and that read-only mode prevents writes until read-write is restored.
