# sources/storage-engines/foundationdb/contrib/mtlsbenchmark/client.sh

## Purpose
This shell script runs the client side of an mTLS handshake benchmark using `fdbserver -r unittests -f :/network/p2ptest`. It connects to a server at `127.0.0.1:4500:tls` for a fixed duration.

## Important APIs, Types, And Functions
The script invokes `/root/build_output/bin/fdbserver` under `taskset -c 0-0`. Important test arguments are `--test_remoteAddresses=127.0.0.1:4500:tls`, `--test_targetDuration=10`, `--test_connectionsOut=10`, `--knob_disable_mainthread_tls_handshake=true`, and `--knob_tls_handshake_flowlock_priority=8900`. TLS arguments point at `keys/ca_file.crt`, `keys/certificate_file.crt`, `keys/key_file.key`, and verify peers with `Root.CN=dummy-ca`.

## Control Flow
There is no argument parsing. Running the script immediately starts one pinned `fdbserver` unittest process configured as the p2ptest client. The command exits when the 10-second target duration completes or the process fails.

## State And Persistence Behavior
The script writes no files directly. The invoked `fdbserver` may emit logs depending on defaults and environment. It reads TLS key material from the relative `keys/` directory.

## Dependencies And Integration Points
It depends on Linux `taskset`, a hard-coded build output at `/root/build_output/bin/fdbserver`, the FoundationDB p2ptest unittest role, a running matching server, and local TLS files. It pairs with `server.sh`.

## Risks And Edge Cases
Hard-coded paths and CPU affinity make it non-portable. Relative TLS paths require running from the benchmark directory. The peer verification pattern is tied to dummy test certificates. No `set -e` or parameterization exists, so failures are only the child command's exit behavior.

## Test Signals
Operational tests should verify the script starts against `server.sh`, completes after roughly 10 seconds, reports successful TLS handshakes, and fails clearly when certificates, server, or `fdbserver` are missing. Static tests can check the hard-coded paths and required certificate files.
