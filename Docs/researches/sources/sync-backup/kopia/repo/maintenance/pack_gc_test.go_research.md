# sources/sync-backup/kopia/repo/maintenance/pack_gc_test.go

Purpose: integration tests deletion of unreferenced pack and session blobs.

Important APIs/types/functions: `TestDeleteUnreferencedPacks`, `verifyBlobExists`, `verifyBlobNotFound`, `mustPutDummyBlob`, and `mustPutDummySessionBlob`.

Control flow: tests create repository data and dummy blobs, run `DeleteUnreferencedPacks` under safety options, and assert which blobs remain or are deleted. Helpers write dummy pack/session blobs and verify blob existence by metadata lookup.

State/persistence behavior: mutates temporary blob storage by adding and deleting pack/session blobs.

Dependencies/integration: uses test HMAC/master keys, content session info encoding, blob APIs, repository environments, and maintenance safety.

Risks/test signals: catches accidental deletion of active-session or too-young blobs and failure to delete eligible orphans. Test data is format-sensitive.
