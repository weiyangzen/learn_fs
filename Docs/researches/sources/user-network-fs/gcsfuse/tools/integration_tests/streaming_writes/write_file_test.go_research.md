# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/write_file_test.go

## Purpose

Tests out-of-order writes against streaming-write files. The goal is to ensure random writes cause the file to synchronize correctly and that deletion after such synchronization removes the remote object.

## Important APIs, control flow, and dependencies

`TestOutOfOrderWriteSyncsFileToGcs` writes `foobar`, verifies local size, writes `foo` at offset 3, validates the preexisting GCS content is still `foobar`, then closes and validates final `foofoo`. `TestOutOfOrderWriteSyncsFileToGcsAndDeletingFileDeletesFileFromGcs` performs the same out-of-order write but removes the file and expects the object to be absent. Dependencies are operation helpers, GCS content/not-found helpers, and `os.Remove`.

## State, persistence, dependencies, and integration points

Out-of-order writes force reconciliation between streamed sequential data and random overwrite data. The tests rely on inherited setup for both local and empty-GCS starting states and inspect remote state before final close/delete.

## Risks and test signals

Risks include losing the first three bytes, prematurely uploading random-write content, or failing to delete the remote object after local removal. Signals are local stat size, pre-close GCS content, final close content, and object-not-found after delete.
