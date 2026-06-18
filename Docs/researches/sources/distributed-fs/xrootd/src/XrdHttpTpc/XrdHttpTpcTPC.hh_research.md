# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.hh

Purpose: Declares the HTTP TPC extension handler, transfer logging record, transfer type enums, and libcurl handle management types.

Important APIs/types/functions: `LogMask`, `TpcType`, `CurlDeleter`, `ManagedCurlHandle`, `TPCHandler`, nested `TPCLogRecord`, static `OSS_TASK_OPAQUE`, and numerous private helpers for curl callbacks, transfer processing, redirects, headers, logging, and digest verification.

Control flow: The class implements `XrdHttpExtHandler::MatchesPath` and `ProcessReq`, then routes to push/pull implementations. Helper declarations mirror the full lifecycle: configure, open local/remote resources, run curl, emit markers, and generate client errors.

State and persistence: Handler fields persist configuration for local/private routing, HTTPS redirects, fixed route, timeouts, CA paths, SFS pointer, temp CA, EC mode, header-to-CGI map, and static monitoring counters. `TPCLogRecord` persists one transfer's monitoring/logging state until destruction.

Dependencies and integration points: Includes XRootD HTTP extension, HTTP utils, TLS temp CA, PMark manager, curl, OpenSSL, and pthread mutex. Exposes the module through `XrdHttpGetExtHandler`.

Risks: Many static and instance settings affect security-sensitive transfer behavior. The nested `TPCLogRecord` holds references to request state and owns a PMark manager, so object lifetime is tied to the request function stack.

Test signals: Header-level compile against current XRootD APIs, plugin ABI symbol lookup, and transfer log record destructor reporting.
