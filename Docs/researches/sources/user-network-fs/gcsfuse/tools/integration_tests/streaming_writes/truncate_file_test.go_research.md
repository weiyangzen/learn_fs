# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/truncate_file_test.go

## Purpose

Provides detailed streaming-write coverage for truncate operations, including pure truncate, invalid negative truncate, write-after-truncate at different offsets, write-then-truncate up and down, write-truncate-write with preserved file offset semantics, and truncate followed by delete.

## Important APIs, control flow, and dependencies

The suite methods call `t.f1.Truncate`, `operations.WriteWithoutClose`, `WriteAt`, `operations.VerifyStatFile`, `CloseFileAndValidateContentFromGCS`, `ValidateObjectContentsFromGCS`, `ValidateObjectNotFoundErrOnGCS`, and `os.Remove`. Test tables encode expected final content with zero-filled holes when truncate extends file size or when subsequent writes occur after the old file offset.

## State, persistence, dependencies, and integration points

The tests are stateful at the file-handle level: truncate changes size but not necessarily the file pointer, stat must reflect local size before upload, and close must materialize zero padding in GCS. `TestTruncateDownAndDeleteFile` also checks that deleting a locally truncated file removes the remote object instead of uploading the truncated content.

## Risks and test signals

Risks include off-by-one zero padding, forgetting that truncate does not move the write pointer, uploading stale pre-truncate data, and inconsistent deletion semantics. Signals are exact stat sizes before upload, exact final strings including `\x00` bytes, expected error on negative truncate, and remote deletion after `os.Remove`.
