# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/streaming_writes_failure/new_local_file_failure_test.go

Purpose: specializes the streaming-write failure suite for a newly created local file with no prior GCS object. It validates object non-existence after failed upload and recovery after block-writer reset.
Important APIs/types/functions: `newLocalFileFailureTestSuite`, `SetupTest`, `validateGcsObject`, and `TestNewLocalFileFailureTestSuite`.
Control flow: setup selects `local_file_2nd_chunk_upload_returns412.yaml`, starts common proxy/mount/storage setup, creates a local file in the mounted test directory, and delegates all failure scenarios to the embedded common suite.
State and persistence: baseline persistent state is absence of `FileName1` in GCS. `validateGcsObject` asserts not-found after failure before a later successful write.
Dependencies and integration points: uses dot-imported client helpers and common failure suite. It relies on proxy skip count for the new-file resumable upload sequence.
Risks and edge cases: local file creation may create unfinalized or placeholder state on zonal/emulator implementations if semantics change. The test assumes non-existence is the correct post-failure state.
Test signals: common tests pass when failures prevent GCS object creation until a fresh handle writes and closes successfully.
