# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecXtractor.hh

Purpose: Defines the HTTP security extractor plugin ABI used to populate `XrdSecEntity` from TLS links, commonly for VOMS or certificate-derived attributes.

Important APIs/types/functions: `XrdHttpSecXtractor` is an abstract base with required `GetSecData(XrdLink *, XrdSecEntity &, SSL *)` and `Init(SSL_CTX *, int)`. Optional `InitSSL` and `FreeSSL` default to failure. The C plugin entry point is `XrdHttpGetSecXtractor(XrdHttpSecXtractorArgs)`, with arguments carrying an error destination, config filename, and namelib parameters.

Control flow: `XrdHttpProtocol::InitSecurity` loads an implementation, calls `Init` with the process TLS context and trace mask, and later authentication calls `GetSecData` per TLS connection.

State and persistence: The interface does not prescribe state. Implementations may keep process-wide config after `Init` and per-SSL state via `InitSSL`/`FreeSSL`.

Dependencies and integration points: Depends on OpenSSL `SSL`/`SSL_CTX`, `XrdLink`, `XrdSecEntity`, and `XrdSysError`. The version-info guidance recommends declaring an XRootD version symbol for ABI compatibility.

Risks: ABI compatibility is sensitive because this is a dynamically loaded plugin interface. Required extractors can reject otherwise valid TLS authentication if VOMS extraction fails. Implementations must be thread-safe at creation and careful with ownership of `XrdSecEntity` strings.

Test signals: Load a minimal extractor, verify `Init` is called, validate successful and failing `GetSecData`, and test required-extractor behavior during TLS client-cert authentication.
