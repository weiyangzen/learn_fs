# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/write_stall_twice_40s.yaml

Purpose: injects two 40-second resumable upload stalls to validate accumulated chunk transfer timeout behavior across multiple retry attempts.
Important keys: same `JsonCreate` and `stall-for-40s-after-15360K` instruction as the single-stall config, with `retryCount: 2` and `skipCount: 2`.
Control flow: after the initial skipped setup calls, two eligible upload requests are stalled. The test expects total elapsed time to reflect two configured chunk-transfer timeouts.
State and persistence: transient proxy counters determine how many upload attempts stall. Completed object state is validated through successful write/sync.
Dependencies and integration points: used by the `MultipleStalls` subcase in `TestChunkTransferTimeout`.
Risks and edge cases: exact elapsed assertions are sensitive to retry scheduling and fixed five-second slack. Any SDK retry/backoff changes may require tolerance adjustment.
Test signals: elapsed sync time should be greater or equal to twice the chunk transfer timeout and less than that plus the slack window.
