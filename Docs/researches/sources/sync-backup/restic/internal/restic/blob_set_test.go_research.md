
# sources/sync-backup/restic/internal/restic/blob_set_test.go

Purpose: tests `BlobSet.String`.

The test starts with an empty set, asserts `"{}"`, inserts a known tree blob and checks the compact `<tree/idprefix>` format, then inserts 100 random data blobs and validates the string with a regexp that expects ten rendered handles and a `(90 more)` suffix.

State is only an in-memory set. Integration value is in diagnostics: prune and checker errors may print blob sets, so stable compact formatting matters for user-facing messages and tests. Risks covered include verbose output for large sets, missing type labels, and unstable ID prefix formatting.
