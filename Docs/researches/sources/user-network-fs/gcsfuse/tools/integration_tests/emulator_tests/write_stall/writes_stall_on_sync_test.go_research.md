# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/writes_stall_on_sync_test.go

Purpose: validates write stall handling, chunk transfer timeout, and chunk retry deadline behavior when resumable uploads stall through the emulator proxy.
Important APIs/types/functions: constants `fileSize` and `stallTime`; suite `chunkTransferTimeoutInfinity`; tests `TestWriteStallCausesDelay`, `TestChunkTransferTimeout`, and `TestChunkRetryDeadline`.
Control flow: suite setup starts a proxy with single 40s stall, mounts with `--chunk-transfer-timeout-secs=0`, writes a 50 MiB file, and asserts `Sync` waits at least 40s. Table-driven tests start proxies for single/multiple stall configs, append proxy endpoint flags, mount, write/sync, and compare elapsed time against parsed flag defaults/overrides. Retry-deadline tests assert success or failure based on deadline.
State and persistence: test files are created in random directories in the emulator bucket. Proxy process/log and mounted state are created and cleaned per subtest.
Dependencies and integration points: uses emulator helper `WriteFileAndSync`, timeout flag parsers, YAML stall configs, setup mount utilities, and `testify`.
Risks and edge cases: mutating `flags` with appended proxy endpoint inside nested loops can leak endpoints across scenarios if reused. Time-based assertions require stable scheduling and emulator behavior.
Test signals: durations near configured timeout windows, success under long deadline, and errors under short deadline validate retry logic.
