
# sources/sync-backup/restic/internal/restic/blob_test.go

Purpose: tests JSON encoding and decoding of `BlobType`.

`TestBlobTypeJSON` iterates `DataBlob` and `TreeBlob`, marshals each to the expected string (`"data"` or `"tree"`), unmarshals back, and asserts equality. It does not cover invalid blob types, which return errors in production code.

State is simple JSON serialization data. Integration points include pack/index JSON representations and any persisted metadata containing blob types. Risks covered include accidental change of persisted blob type names and unmarshal drift. Missing test coverage: invalid JSON/type values and `InvalidBlob` marshal behavior.
