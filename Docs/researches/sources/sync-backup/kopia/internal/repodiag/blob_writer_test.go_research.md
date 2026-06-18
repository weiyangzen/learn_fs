# sources/sync-backup/kopia/internal/repodiag/blob_writer_test.go

Purpose: verifies diagnostic writer encryption and storage output.

Important APIs/types/functions: `TestDiagWriter` and `newStaticCrypter`.

Control flow: creates a map storage and static crypter, writes diagnostic data asynchronously, waits, then asserts expected encrypted blob content exists.

State and persistence behavior: in-memory blob storage receives encrypted output.

Dependencies and integration points: validates `BlobWriter` behavior without a real repository.

Risks and test signals: focuses on happy path; error-path tests should simulate storage write and crypter failures.
