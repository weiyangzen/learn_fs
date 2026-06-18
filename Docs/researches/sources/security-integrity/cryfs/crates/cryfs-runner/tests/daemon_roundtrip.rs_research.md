# sources/security-integrity/cryfs/crates/cryfs-runner/tests/daemon_roundtrip.rs

## Purpose
End-to-end integration test for repeated RPC request/response exchanges with the fork+exec helper daemon.

## Important APIs, types, and functions
- Defines local `Request` and `Response` payloads.
- Uses `CARGO_BIN_EXE_cryfs-runner-test-background` and `start_background_process_with_exe`.
- Single test `roundtrip_many_requests`.

## Control flow
The test starts the helper in `echo` mode, sends ten sequential requests, waits up to five seconds for each response, and asserts each response increments the request value. Dropping the client at the end should close pipes and let the helper exit cleanly.

## State and persistence behavior
No disk persistence. State is the live daemon process and pipe streams.

## Dependencies and integration points
Exercises spawn, fd mapping, typed RPC, postcard encoding, and EOF-on-client-drop behavior at process boundary.

## Risks and edge cases
Payload sizes are simple `i32`; large payload behavior is covered by pipe unit tests instead. The test does not explicitly wait/reap the helper; it relies on helper EOF handling after client drop.

## Test signals
Ten successful sequential responses and no hang on client drop indicate the daemon loop and pipe framing remain healthy.
