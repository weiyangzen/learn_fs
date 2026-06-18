# sources/storage-engines/foundationdb/contrib/mtlsbenchmark/server.sh

## Purpose
This shell script runs the server side of the mTLS handshake benchmark using FoundationDB's p2ptest unittest mode. It listens indefinitely on TLS port 4500.

## Important APIs, Types, And Functions
The script invokes `/root/build_output/bin/fdbserver` under `taskset -c 1-1` with `--test_listenerAddresses=0.0.0.0:4500:tls`, `--test_targetDuration=0`, `--knob_tls_handshake_limit=1000`, `--knob_tls_server_handshake_threads=1`, `--knob_disable_mainthread_tls_handshake=true`, `--knob_tls_handshake_flowlock_priority=8900`, and `--knob_tls_handshake_timeout_seconds=3.0`. It uses the same CA, certificate, key, and verify-peers pattern as the client.

## Control Flow
Running the script immediately starts a pinned p2ptest server. With target duration 0, it runs until interrupted or until the process exits due to an error.

## State And Persistence Behavior
The script itself is stateless. The child process listens on all interfaces at port 4500 and reads TLS files from `keys/`. Logs/output are inherited from the shell environment.

## Dependencies And Integration Points
It depends on Linux `taskset`, hard-coded `/root/build_output/bin/fdbserver`, p2ptest support, available port 4500, and local test certificates. It is intended to be started before `client.sh`.

## Risks And Edge Cases
Listening on `0.0.0.0` exposes the test TLS endpoint beyond localhost if firewall rules allow it. Hard-coded root build paths and CPU pinning limit reuse. The script has no cleanup, readiness probe, or parameterization. The dummy peer verification pattern is not production-safe.

## Test Signals
Tests should verify the server binds to port 4500, accepts the client benchmark, enforces certificate presence, respects the handshake thread/timeout knobs, and exits nonzero when the port is occupied or `fdbserver` is missing.
