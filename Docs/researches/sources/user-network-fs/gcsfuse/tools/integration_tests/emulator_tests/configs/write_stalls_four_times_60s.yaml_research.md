# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stalls_four_times_60s.yaml

Purpose: injects four long resumable upload stalls to validate `--chunk-retry-deadline-secs` success and failure boundaries.
Important keys: `JsonCreate`, `stall-for-60s-after-15360K`, `retryCount: 4`, and `skipCount: 2`.
Control flow: first four eligible upload attempts stall. Tests combine this with a 10-second chunk transfer timeout so the client accumulates about 40 seconds of failed attempts before the next attempt can succeed, unless the retry deadline is shorter.
State and persistence: proxy counters are runtime-only. The outcome is either a completed object after retries or an error before completion.
Dependencies and integration points: consumed by `TestChunkRetryDeadline`.
Risks and edge cases: assumes transfer timeout, retry deadline, and proxy stall durations interact deterministically. Slow hosts may blur elapsed-time expectations.
Test signals: deadline 120s should succeed after the induced retry sequence; deadline 32s should fail with a sync/write error.
