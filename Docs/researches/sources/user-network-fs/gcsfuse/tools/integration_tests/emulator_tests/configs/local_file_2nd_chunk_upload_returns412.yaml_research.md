# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/local_file_2nd_chunk_upload_returns412.yaml

Purpose: proxy fault-injection config for streaming writes to a new local file. It returns 412 on the second chunk upload without an existing GCS object.
Important keys: `targetHost`, `retryConfig` for `JsonCreate`, `retryInstruction: return-412`, `retryCount: 1`, and `skipCount: 3`.
Control flow: the proxy skips test directory creation, resumable upload session creation, and first chunk upload, then injects the 412 into the next matching JSON create/upload request.
State and persistence: proxy counters are transient. The expected persistent result is that no completed GCS object exists after the failed upload path.
Dependencies and integration points: used by `new_local_file_failure_test.go` through the common failure suite and storage client bound to the proxy endpoint.
Risks and edge cases: skip count is request-sequence-sensitive and may break if gcsfuse creates additional objects or the SDK changes resumable upload flow.
Test signals: failure tests should produce write errors and `ValidateObjectNotFoundErrOnGCS` should pass before block-writer reinitialization.
