# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_40s.yaml

Purpose: injects a single 40-second stall during resumable JSON write upload after 15 MiB, for chunk-transfer timeout and infinite-timeout tests.
Important keys: `targetHost`, `retryConfig` method `JsonCreate`, `retryInstruction: stall-for-40s-after-15360K`, `retryCount: 1`, and `skipCount: 2`.
Control flow: the proxy skips initial file creation and resumable upload session creation, then stalls the first actual upload request matching the threshold.
State and persistence: proxy tracks injected count; test file data persists in the emulator bucket if retries succeed.
Dependencies and integration points: used by `writes_stall_on_sync_test.go` scenarios `SingleStall` and `chunkTransferTimeoutInfinity`.
Risks and edge cases: relies on a 50 MiB file and upload chunking crossing the 15 MiB point. Upload block size changes can alter where the stall is triggered.
Test signals: sync duration is at least 40 seconds for infinite timeout, or bounded near configured timeout for retry-enabled scenarios.
