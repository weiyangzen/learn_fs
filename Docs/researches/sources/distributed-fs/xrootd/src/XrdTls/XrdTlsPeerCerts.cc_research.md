# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsPeerCerts.cc

Purpose: Implements ownership behavior for XrdTlsPeerCerts.

Important APIs/types/functions: Destructor frees cert with X509_free() when present. getCert(bool upref) optionally increments the X509 reference count with X509_up_ref() before returning the cert pointer.

Control flow: XrdTlsSocket::getCerts() constructs this wrapper with SSL_get_peer_certificate() and SSL_get_peer_cert_chain(). The wrapper owns the peer cert reference but not the chain.

State/persistence: The object holds borrowed/owned pointers only for the lifetime of the TLS session/wrapper. No persistence.

Dependencies/integration: Depends on OpenSSL X509 and XrdTlsPeerCerts.hh. Consumers must observe the ownership contract from the header.

Risks: Passing getCert(false) to code that frees the certificate can double-free when the wrapper is destroyed. getChain() returns a session-owned chain, invalid after SSL_free().

Test signals: Reference-count tests around getCert(true), wrapper destruction, and using chain before/after socket shutdown with sanitizer instrumentation.
