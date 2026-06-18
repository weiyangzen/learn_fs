# sources/test-tools/syzkaller/syz-ci/manager_test.go

Purpose: unit tests for selected syz-ci manager behaviors.

Important APIs/types/functions: `dashapiMock`, `TestManagerPollCommits`, `TestUploadCoverJSONLToGCS`, and `mockWriteCloser`.

Control flow: commit test builds a temporary git repo with matching and fix-tag commits, mocks dashboard `BuilderPoll`, repeatedly samples pending commits, and verifies found titles/fix commits. Coverage test serves JSONL from httptest, mocks GCS writes, exercises upload suffix/compression/publish/error cases, and inspects resulting content.

State and persistence: temporary git repos, HTTP server, and in-memory mock writes.

Dependencies and integration points: validates `Manager.pollCommits` and streaming upload path with GCS mock.

Risks: does not exercise real dashboard, real GCS, actual manager HTTP coverage generation, or asset storage upload.

Test signals: strong focused coverage for commit sampling/fix extraction and JSONL upload transformations.
