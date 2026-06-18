## sources/sync-backup/restic/internal/repository/index_list_test.go

Purpose: validates streaming index blob enumeration.

Important tests: `TestAllIndexBlobs` creates a repository, saves five data blobs, loads the master index, compares master `ListBlobs` output with `AllIndexBlobs` output. `TestAllIndexBlobsEarlyStop` saves blobs, breaks after one streamed entry, and asserts no error is yielded after early stop.

Control flow and state: tests save blobs through `WithBlobUploader`; the first test explicitly loads the master index for baseline comparison.

Dependencies and integration points: exercises repository uploader/index persistence plus direct index streaming.

Risks and test signals: tests cover happy path and early stop, not decode errors or context cancellation.
