# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/read_stall_5s.yaml

Purpose: injects a controlled XML read stall for read-stall retry tests. It makes the first eligible read hang for five seconds immediately after zero kilobytes.
Important keys: `targetHost`, `retryConfig` method `XmlRead`, `retryInstruction: stall-for-5s-after-0K`, `retryCount: 1`, and `skipCount: 0`.
Control flow: the proxy stalls the first read, allowing tests to verify that gcsfuse's read-stall retry timeout cancels/retries before the full stall elapses.
State and persistence: no persistent state beyond proxy counters/logs. File data is created in the emulator bucket by the test.
Dependencies and integration points: consumed by `read_stall_test.go` through `StartProxyServer` and `AppendProxyEndpointToFlagSet`.
Risks and edge cases: timing assertions depend on scheduler and emulator responsiveness; if stall injection moves to a different protocol path the test may not exercise retry logic.
Test signals: first-byte read elapsed time should exceed configured minimum timeout but stay below the forced five-second stall.
