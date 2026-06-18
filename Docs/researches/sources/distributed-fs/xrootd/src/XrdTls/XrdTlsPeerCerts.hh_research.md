# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.hh

Purpose: Declares a small wrapper for a peer certificate and its peer certificate chain.

Important APIs/types/functions: XrdTlsPeerCerts(X509 *, STACK_OF(X509) *) stores the certificate and chain. getCert(upref) returns the certificate and can increment its reference count. getChain() returns the chain pointer. hasCert() and hasChain() expose presence checks.

Control flow: The object is created by XrdTlsSocket::getCerts() after optional verification. Callers delete it when done.

State/persistence: Holds one cert pointer and one chain pointer. The cert is owned by the wrapper; the chain is borrowed from the SSL session.

Dependencies/integration: Includes OpenSSL SSL for X509 stack types. It bridges XrdTlsSocket with security plugins needing certificate material.

Risks: The ownership asymmetry is easy to misuse. The header explicitly warns that many opaque APIs free certs and therefore require getCert(true). The chain lifetime is tied to the SSL session, not this wrapper.

Test signals: API tests should cover null cert/chain, hasCert/hasChain, upref failure handling, and caller ownership scenarios.
