# sources/sync-backup/kopia/repo/blob/storage_extend_test.go

Purpose: format-version matrix tests for repository-level blob retention extension behavior.

Important APIs/types/functions: methods on `formatSpecificTestSuite` are `TestExtendBlobRetention` and `TestExtendBlobRetentionUnsupported`. They use repotesting environments, object writers, fake time, encryption/HMAC settings, `blob.ListAllBlobs`, `RetentionStorage.GetRetention`, and `BlobStorage().ExtendBlobRetention`.

Control flow: the positive test creates a repository with retention enabled, writes and flushes an object, checks that the last blob has governance retention near the expected expiry, extends retention, and verifies the new expiry. The unsupported test creates a repository without retention, writes data, then expects `object locking unsupported` from `ExtendBlobRetention`.

State and persistence behavior: tests write real repository format blobs and pack/index blobs into test storage for each supported format version. Fake time controls expected retention timestamps.

Dependencies/integration: integrates repo creation/open options, encryption formats, content/object writing, root storage retention hooks, and the blob retention API.

Risks and edge cases: test assumes a fixed count of four blobs after the write/flush sequence. It verifies the last blob only, so broader retention coverage depends on repository writer behavior.

Test signals: success confirms retention configuration reaches storage writes and that unsupported retention remains a clear sentinel error across format versions.
