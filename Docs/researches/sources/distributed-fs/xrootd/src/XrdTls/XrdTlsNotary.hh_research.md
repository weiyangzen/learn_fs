# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsNotary.hh

Purpose: Declares the hostname validation policy wrapper used by client TLS connections.

Important APIs/types/functions: XrdTlsNotary::Validate() validates a hostname against a peer SSL certificate and optional XrdNetAddrInfo for DNS fallback. UseCN(bool) controls whether Common Name fallback is permitted. Static cnOK stores that policy.

Control flow: The comments define policy order: SAN match first, CN fallback when allowed, then optional reverse DNS fallback if netInfo is supplied. The returned const char * is null on success or a diagnostic reason on failure.

State/persistence: Only static cnOK policy state.

Dependencies/integration: Includes openssl/ssl.h and forward declares XrdNetAddrInfo. XrdTlsSocket::Connect() uses this API after SSL_connect().

Risks: Since Validate() returns string literals/internal diagnostics, callers must not free the return. cnOK is global and not synchronized, so configure it at process initialization. The documented DNS fallback must be evaluated carefully in deployments with mutable reverse DNS.

Test signals: Public API tests should assert null/non-null semantics and verify UseCN(false) changes no-SAN certificate behavior.
