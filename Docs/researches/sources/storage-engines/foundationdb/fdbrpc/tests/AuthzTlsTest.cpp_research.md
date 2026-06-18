# sources/storage-engines/foundationdb/fdbrpc/tests/AuthzTlsTest.cpp

## Purpose
`AuthzTlsTest.cpp` is a standalone non-Windows TLS authorization integration test for fdbrpc. It forks a server and client using real `Net2` and `FlowTransport`, generates in-memory certificates, probes whether the server sees the peer as trusted, and verifies expected outcomes across TLS, no-TLS, expired certificate, missing certificate, and password-protected key cases.

## Important APIs, Types, And Functions
Key test enums are `ExitCodes`, `Role`, `ChainLength` with `NO_TLS = -1`, and `Result` (`ERROR`, `TRUSTED`, `UNTRUSTED`, `TIMEOUT`). `TLSCreds` carries PEM bytes and password state. `makeCreds` generates certificate chains or password-protected certs through `mkcert`. `SessionInfo`, `SessionProbeRequest`, and `SessionProbeReceiver` define a small fdbrpc request/response protocol; the receiver reads `FlowTransport::transport().currentDeliveryPeerIsTrusted()` and `currentDeliveryPeerAddress()`. `runHost<IsServer>` starts either a server or client transport. `runTlsTest` sets up credentials, pipes, forked children, stdout capture, and process status checking. `main` generates a matrix of chain-length categories plus password tests.

## Control Flow
For each test case, the main process creates pipes and forks the server. The server configures `TLSConfig`, binds `FlowTransport` to `127.0.0.1:0` or `:tls`, registers the probe endpoint, starts the network in a thread, writes its bound address and endpoint token to the address pipe, then waits for a completion flag. The main process then forks the client. The client reads the server address/token, adjusts the TLS flag according to its credentials, sends a `SessionProbeRequest`, runs the network until either a reply or timeout, writes completion to the server, and exits with a status matching the expected result. The parent drains child stdout, waits for both subprocesses, and records failed cases.

## State And Persistence Behavior
The test uses process-local globals (`role`, `g_network`) in each forked process. Certificates are generated in memory and passed by value before fork. Pipes carry the server network address, endpoint token, and completion signal. Trace files are opened in the working directory with client/server prefixes. There is no persistent product state, but subprocess and pipe cleanup is critical to avoid hangs.

## Dependencies And Integration Points
The test depends on POSIX APIs (`fork`, `pipe`, `dup2`, `waitpid`, `read`, `write`), `fmt`, Flow errors and arenas, `mkcert`, `TLSConfig`, `newNet2`, `openTraceFile`, and `FlowTransport`. It is built only when not on Windows and is registered in CTest by `fdbrpc/tests/CMakeLists.txt` as `authorization_tls_unittest` with a 120 second timeout.

## Risks And Test Signals
The test has blocking pipe reads/writes that are acceptable for this controlled scenario but can hang if child startup fails before pipe closure. It relies on raw `NetworkAddress` and endpoint token writes across forked processes; a static assertion covers trivial destructibility for `NetworkAddress`, but this is still tightly coupled to object layout. Randomized chain lengths use `std::rand`, so failures need the printed seed. Passing output ends with `Test OK`; failure logs include specific chain pairs, password cases, subprocess exit codes, and waitpid messages.
