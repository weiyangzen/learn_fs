# sources/distributed-fs/tahoe-lafs/integration/test_get_put.py

## Purpose
Integration coverage for Tahoe CLI upload/download paths, especially binary data through stdin/stdout, large immutable files, and compatibility between old and current immutable segment-size defaults.

## Important APIs, Types, and Functions
`DATA` is intentionally non-UTF-8 binary input. `get_put_alias` creates the `getput:` alias once per session through `util.cli`. `read_bytes` verifies byte-preserving output. The tests use `subprocess.Popen`, `check_call`, and `check_output` directly for stream-oriented CLI behavior, plus `blockingCallFromThread` to call `alice.reconfigure_zfec` from tests decorated with `run_in_thread`.

## Control Flow
The stdin test starts `tahoe put - getput:fromstdin`, writes `DATA` to the child stdin, waits for exit code 0, then downloads to a temp file. The stdout test uploads from a temp file, then runs `tahoe get getput:tostdout -` and compares stdout bytes. The large-file test writes `DATA * 1_000_000`, uploads it by path, downloads by path, and compares full file bytes. The segment-size test uploads and downloads the same multi-megabyte payload while toggling `shares._max_immutable_segment_size_for_testing` between 1 MiB and 128 KiB.

## State and Persistence
The alias and remote objects persist inside Alice's Tahoe node for the test session. The segment-size test mutates Alice's `tahoe.cfg` and restarts the node via `reconfigure_zfec`, so later tests depending on the same fixture may observe changed ZFEC state unless their fixtures reset it.

## Dependencies and Integration Points
Depends on the `tahoe` executable, Alice's node directory, Twisted reactor interop, and the Tahoe CLI semantics for `put`, `get`, aliases, stdin `-`, and stdout `-`.

## Risks
Direct subprocess use bypasses the common `util.run_tahoe` error wrapper in several tests. Large stdout comparisons can be memory-heavy. Reconfiguration is reactor-sensitive and may be platform-sensitive, especially because tests run blocking code in worker threads.

## Test Signals
Strong signals are exact byte equality, successful process exit codes, and cross-version segment-size compatibility for immutable uploads.
