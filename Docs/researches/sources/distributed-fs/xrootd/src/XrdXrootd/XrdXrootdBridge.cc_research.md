# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.cc

Purpose: provides the concrete entry point for creating an xrootd protocol bridge session for non-xrootd protocol frontends. The implementation delegates bridge creation to the transit protocol layer.

Important APIs and functions: `XrdXrootd::Bridge::Login()` accepts a result callback object, an `XrdLink`, a security entity, a short client name, and protocol name. It returns `XrdXrootdTransit::Alloc(...)`, typed as `Bridge*`.

Control flow and state: there is no local persistent state in this file. It is intentionally a thin factory, keeping the public bridge API decoupled from the actual transit implementation.

Dependencies and integration: includes `XrdXrootdBridge.hh` and `XrdXrootdTransit.hh`. The bridge API is used by other protocol stacks such as HTTP-style frontends that need to inject xrootd-format requests and rewrite responses through `Bridge::Result`.

Risks and test signals: failures depend on `XrdXrootdTransit::Alloc()` semantics, not on this wrapper. Tests should verify login propagates null/error conditions correctly and that transit allocation receives the exact callback, link, security, name, and protocol arguments.
