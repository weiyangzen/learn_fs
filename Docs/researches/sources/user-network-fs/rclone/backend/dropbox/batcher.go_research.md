# sources/user-network-fs/rclone/backend/dropbox/batcher.go

## Purpose
`batcher.go` implements the Dropbox backend's synchronous batch commit path for upload sessions. Dropbox permits many upload batches to be started, but only one batch may be committed at a time, so this file provides the commit helper used by the backend's batcher.

## Important APIs, types, and functions
- `finishBatch` wraps `UploadSessionFinishBatchV2`, pacing/retrying the API call and returning a batch result.
- `commitBatch` calls `finishBatch`, validates the number of returned entries, and maps each Dropbox per-entry result into either a `*files.FileMetadata` result slot or an error slot.

## Control flow
`commitBatch` receives ordered upload finish arguments plus parallel result/error slices supplied by the caller. It finalizes the batch with Dropbox, checks that Dropbox returned exactly one entry per requested item, then iterates entries by index. Success entries populate `results[i]`; failed entries build a descriptive error tag from the top-level tag and nested failure, lookup, path, or properties tags and store it in `errors[i]`.

## State and persistence behavior
The persistent effect is on Dropbox: upload sessions are committed into real files. Locally, the function mutates caller-provided result and error slices in place. No durable local state is written here.

## Dependencies and integration points
This file depends on the Dropbox SDK `files` package, the backend `Fs` pacer, `f.srv.UploadSessionFinishBatchV2`, and the backend-specific `shouldRetryExclude` retry classifier. It is part of the Dropbox upload pipeline outside this file.

## Risks and edge cases
- Return order is assumed to align with request order; wrong ordering would misassign results.
- A mismatch in returned entry count aborts the whole commit with an error.
- Retry policy intentionally retries all errors after the first chunk except excluded errors; misclassification can duplicate expensive commits or fail too early.
- Error reporting compresses nested Dropbox failure information into a string tag, which is useful but may omit full structured details.

## Test signals
No tests are included in this subset for `batcher.go`. Coverage likely comes from Dropbox backend upload integration tests. Key test cases should include mixed success/failure batches, returned entry count mismatch, nested failure tags, and retry-excluded errors.
