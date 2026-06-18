
# sources/sync-backup/restic/internal/restic/ids_test.go

Purpose: tests compact `IDs.String` formatting.

`TestIDsString` constructs three IDs, including a duplicate, and asserts the output contains 8-character prefixes in slice order inside brackets. The duplicate remaining duplicated is intentional because `IDs` is a list, not a set.

State is local ID values. Integration points are diagnostic output in repair and repository code. Risks covered include formatting drift and accidental deduplication in list rendering.
