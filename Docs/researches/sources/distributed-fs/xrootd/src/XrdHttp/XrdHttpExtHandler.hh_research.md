## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.hh

Purpose: defines the external HTTP handler plugin ABI and the request object supplied to plugins.

Important APIs/types: `XrdHttpExtReq` exposes HTTP verb/resource, mutable headers reference, client identity fields, length, packet-marking handle, TPC credential-forwarding flag, SciTag, Repr-Digest and Want-Repr-Digest maps, security entity access, request body buffer access, and response-sending helpers. `XrdHttpExtHandler` is an abstract base with `MatchesPath()`, `ProcessReq()`, and `Init()`. The header declares the required plugin factory `XrdHttpGetExtHandler()` and `XrdHttpExtHandlerArgs` macro.

State and persistence: plugin state is owned by concrete handlers; the request object is per-request adapter state and references protocol/request internals.

Dependencies and integration: private installed header for HTTP extension plugins. It depends on `XrdNetPMark`, forward-declared XRootD protocol/security types, and the XRootD version-info convention for plugin ABI tracking.

Risks and test signals: this is ABI-facing; field layout and virtual method changes can break plugins. Tests should include building a minimal plugin, path matching, request processing, factory symbol loading, and version-info declaration compatibility.
