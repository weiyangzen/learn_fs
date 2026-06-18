# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpSecurity.cc

Purpose: Implements HTTP TLS security initialization and client-certificate authentication for `XrdHttpProtocol`, including grid-map lookup and optional security extractor integration.

Important APIs/types/functions: `InitSecurity` initializes the ssl crypto factory, grid-map service, and optional sec extractor. `HandleAuthentication` validates the OpenSSL peer result, parses the peer certificate chain, stores the DN in `SecEntity.moninfo`, invokes VOMS extraction, and delegates name mapping. `HandleGridMap` maps certificate DN to a local user or fallback name. `GetVOMSData` calls the extractor and preserves gridmap-derived names when needed.

Control flow: Initialization obtains `XrdCryptoFactory::GetCryptoFactory("ssl")`, loads `XrdOucGMap` if `gridmap` is configured, and initializes the extractor with `xrdctx->Context()`. During authentication, OpenSSL verification failure returns an error. Missing peer cert returns success with no identity. A valid chain yields DN and hash, VOMS data extraction, optional required-extractor enforcement, and grid-map or fallback identity assignment.

State and persistence: Static `servGMap` and `myCryptoFactory` persist for the process. Per-connection authentication mutates `SecEntity.moninfo`, `SecEntity.name`, entity attributes, and link ID. No durable state is written.

Dependencies and integration points: Uses `XrdTlsPeerCerts`, `XrdTlsContext`, `XrdCryptoX509Chain`, `XrdCryptoFactory`, `XrdOucGMap`, `XrdSecEntityAttr`, OpenSSL, and the `XrdHttpSecXtractor` ABI. `TRACEI`/`eDest` report security diagnostics.

Risks: Fallback identity generation from DN/CN is compatibility-driven and can produce surprising names if gridmap is absent. Memory ownership of `SecEntity` string fields is manual. Required gridmap/extractor settings turn mapping failures into hard authentication failures. OpenSSL context access is noted as undesirable in the source comment.

Test signals: Certificate-present and certificate-absent TLS cases, gridmap success/failure with required and optional modes, extractor success/failure, fallback hash/CN naming, and cleanup of replaced `SecEntity.moninfo/name`.
