## sources/sync-backup/restic/internal/repository/index_testutil_test.go

Purpose: repository-package test utility for retrieving blobs belonging to one pack from the loaded master index.

Important APIs: `BlobsInPack(repo, packID)` iterates `repo.idx.Values()`, filters entries whose pack ID matches, appends their `pack.Blob`, sorts by offset, and returns them.

Control flow and state: read-only helper over an already loaded repository index. It assumes `repo.idx` is populated by the caller.

Dependencies and integration points: used by repository tests outside this target set that need pack blob layout without duplicating index iteration logic.

Risks and test signals: if the repository index is not loaded, the helper can return incomplete results. It is test-only and has no dedicated test.
