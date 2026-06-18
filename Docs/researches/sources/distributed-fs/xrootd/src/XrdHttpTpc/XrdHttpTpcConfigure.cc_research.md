# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcConfigure.cc

Purpose: Parses HTTP TPC plugin configuration and initializes filesystem, TLS CA, logging, routing, and transfer policy state.

Important APIs/types/functions: `TPCHandler::Configure` reads directives such as `http.desthttps`, `tpc.allow`, `tpc.deny`, `tpc.trace`, `tpc.fixed_route`, `tpc.header2cgi`, and `tpc.timeout`. `ConfigureLogger` maps trace words to `LogMask` bits.

Control flow: The config stream captures HTTP TPC directives, validates each directive, updates handler fields, removes `authorization` from `hdr2cgimap`, initializes CA/CRL material from `http.cadir`/`http.cafile` or `XRDTPC_CADIR`, and obtains `XrdSfsFileSystem*` from the environment.

State and persistence: Mutates handler instance fields for allow/deny private/local routing, HTTPS redirect preference, fixed-route mode, timeouts, CA paths, CA temp file, `usingEC`, CRL policy, SFS pointer, and header-to-CGI map. `XrdTlsTempCA` may create temporary CA/CRL artifacts managed by that helper.

Dependencies and integration points: Uses `XrdOucStream`, `XrdOuca2x`, `XrdOucEnv`, `XrdTlsTempCA`, `XrdHttpProtocol::parseHeader2CGI`, environment variables, and the XRootD SFS object.

Risks: A bad directive aborts plugin configuration. `http.desthttps` validation error text says `https.desthttps`, a minor diagnostic mismatch. Missing SFS object is fatal. `XRDTPC_CADIR` bypasses temp CA generation and CRL workaround behavior.

Test signals: Config parse success/failure for every directive, header2cgi authorization removal, timeout defaults, CA/CRL setup with empty CRLs, environment overrides, and absence of SFS pointer.
