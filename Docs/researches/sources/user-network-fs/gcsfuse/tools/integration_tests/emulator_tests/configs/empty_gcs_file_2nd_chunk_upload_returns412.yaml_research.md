# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/empty_gcs_file_2nd_chunk_upload_returns412.yaml

Purpose: proxy fault-injection config for streaming-write failure tests against an existing empty GCS object. It forces a 412 response during the second chunk upload path.
Important keys: `targetHost` points to the HTTP testbench; `retryConfig` targets `JsonCreate`, uses `retryInstruction: return-412`, `retryCount: 1`, and `skipCount: 4`.
Control flow: the proxy ignores the first four matching calls because they create the test directory, create the empty object, create the resumable upload URI, and upload the first chunk. The next eligible `JsonCreate` returns 412.
State and persistence: no persisted state beyond proxy counters. It is designed so the original empty GCS object remains unchanged after write failure.
Dependencies and integration points: consumed by `empty_gcs_file_failure_test.go` through `commonFailureTestSuite.setupTest` and `StartProxyServer`.
Risks and edge cases: the skip count is tightly coupled to the storage client's request sequence. SDK/protocol changes can shift call counts and make the injected failure hit the wrong request.
Test signals: streaming-write tests should see write/sync/close failures while GCS validation still finds an empty object.
