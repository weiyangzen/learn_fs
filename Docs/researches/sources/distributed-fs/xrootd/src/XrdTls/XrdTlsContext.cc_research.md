# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.cc

Purpose: Implements XrdTlsContext, the owner of OpenSSL SSL_CTX objects, TLS library initialization, certificate/key/CA validation, CRL refresh, session creation, session cache settings, and runtime client-auth toggling.

Important APIs/types/functions: XrdTlsContextImpl stores ctx, pending ctxnew, CTX_Params, crlMutex, flusher condition variable, refresh flags, lastCertModTime, and session cache replay state. XrdTlsCrl::Refresh() periodically clones contexts when CRLs or host certs change. XrdTlsFlush::Flusher() flushes OpenSSL session cache. InitTLS() initializes OpenSSL. VerPaths() validates filesystem permissions. verifyPeerCB() logs verification failures and can soft-fail missing CRLs when crlAM is set. Constructor, Clone(), Session(), SessionCache(), SetContextCiphers(), SetDefaultCiphers(), SetCrlRefresh(), x509Verify(), newHostCertificateDetected(), and SetTlsClientAuth() form the main behavior.

Control flow: Construction initializes debug/OpenSSL once, fills CA/cert paths from explicit parameters or environment for client contexts, validates paths, creates SSL_CTX with TLS_method(), sets secure options, loads CA locations and verification flags, sets ciphers, loads certificate/private key, starts CRL refresh if requested, and keeps the ctx. Session() fast-paths SSL_new(ctx) but, if ctxnew exists, swaps in the refreshed SSL_CTX under a write lock, repairs ex_data to point at the surviving owner, creates a session, and deletes the replacement wrapper.

State/persistence: State is process-local. Persistent inputs are cert/key/CA files and environment variables X509_CERT_DIR, X509_CERT_FILE, X509_USER_KEY, X509_USER_PROXY, XRDTLS_DEBUG. CRL and certificate changes are detected by periodic refresh and stat modification time.

Dependencies/integration: Depends on OpenSSL SSL/BIO/ERR/X509, XrdOucUtils path/modtime helpers, XrdSys locks/threads/timers, XrdTls diagnostics, and XrdTlsTrace. XrdTlsSocket consumes Session() and GetParams().

Risks: Thread lifetime is delicate: destructor may leave pImpl for refresh/flusher threads to delete. Session() swaps SSL_CTX ownership and nulls ctxnew->pImpl->ctx to avoid double free. The CRL refresh loop clones contexts outside locks and must handle construction failure without losing the existing ctx. Permission masks in VerPaths() are security-sensitive.

Test signals: Test client/server context creation with explicit and env-derived paths, invalid permissions, missing CA in client mode, CRL soft fail, logVF output, cert/key mismatch, CRL refresh swap, host certificate modtime refresh, session cache id/flush options, and SetTlsClientAuth toggling.
