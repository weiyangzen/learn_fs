# sources/distributed-fs/xrootd/src/XrdTls/XrdTlsContext.hh

Purpose: Declares XrdTlsContext, the public wrapper around OpenSSL SSL_CTX and TLS configuration options.

Important APIs/types/functions: CTX_Params records cert, pkey, cadir, cafile, opts, and crlRT. Public methods include Clone(), Context(), GetParams(), Init(), isOK(), Session(), SessionCache(), SetContextCiphers(), SetDefaultCiphers(), SetCrlRefresh(), SetTlsClientAuth(), x509Verify(), newHostCertificateDetected(), and the constructor/destructor. Option masks define handshake timeout, verify depth, log verification failures, server mode, DNS fallback, proxy-cert policy, CRL refresh/checking/full-chain checking, CRL soft-fail, auto-retry, and client-cert request disabling. TLS_SET_HSTO, TLS_SET_REFINT, and TLS_SET_VDEPTH pack option fields.

Control flow: The header documents that callers construct, immediately check isOK(), then request sessions through Session() for socket wrappers. Clone() can remove verification when full=false or start CRL refresh on the clone.

State/persistence: Runtime state is hidden behind XrdTlsContextImpl. Configuration state is captured in CTX_Params and exposed read-only by pointer.

Dependencies/integration: Forward declares XrdTlsSocket and XrdSysLogger. The ctxIndex static is used by OpenSSL ex_data callbacks in the implementation.

Risks: Option fields are ABI/API contracts. Some comments have drift from implementation, for example session cache replay in Clone() is now implemented. Context() exposes the raw SSL_CTX and bypasses locking constraints noted in the implementation.

Test signals: Compile public consumers, verify option macros preserve unrelated bits, and validate that comments about client/server CA behavior match constructor outcomes.
