<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/TLSTest.cpp -->
# sources/storage-engines/foundationdb/flow/TLSTest.cpp
- Purpose: Standalone Boost.Asio TLS handshake test program using generated certificate chains.
- Important APIs/types/functions: `runTlsTest`, `trustRootCaCert`, `useChain`, `initCerts`, `initSslContext`, logging helpers, endpoint formatter, and `main`.
- Control flow: For each server/client chain-length pair, it builds valid or intentionally expired cert chains, initializes client/server contexts, starts a loopback accept/connect pair, performs async handshakes, tracks whether verification callbacks considered peers trusted, then asserts expected handshake and trust outcomes.
- State and persistence behavior: State is local to each test run: generated certs in arenas, socket state enums, work guards, and `handshakeOk`. It writes human-readable logs to `outp`.
- Dependencies and integration points: Depends on Boost.Asio, Boost SSL, Flow `MkCert`, `Arena`, and assertions. It validates the certificate-chain mechanics used by TLS configuration code but does not directly use `TLSPolicy`.
- Risks: As a standalone `main`, it may not run with normal `TEST_CASE` infrastructure. Async ordering is simple but shared `handshakeOk` is mutated from callbacks on one `io_context`. Expectations are tied to how server endpoint treats absent client certs.
- Test signals: The hard-coded matrix covers valid chains, absent client/server certs, and expired certs on either side. Failures appear as assertion mismatches or logged handshake errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/TLSTest.cpp -->
