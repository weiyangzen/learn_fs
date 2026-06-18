# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdBridge.hh

Purpose: defines the public bridge interface that lets another request/response protocol reuse the xrootd protocol stack. It documents threading constraints, request injection, response rewriting, sendfile handoff, wait handling, and teardown.

Important APIs and types: `Bridge::Login()` creates a session bridge. Virtual `Run()` injects a network-format xrootd request plus optional data. `Disc()` disbands the bridge. `setSF()` toggles sendfile for an open handle. `SetWait()` configures wait handling. `Bridge::Context` carries link, request code, and stream id and has a virtual `Send()` for completing a pending sendfile response. `Bridge::Result` defines callbacks: `Data()`, `Done()`, `Error()`, `File()`, `Free()`, `Redir()`, `Wait()`, and `WaitResp()`.

Control flow and state: the API models asynchronous execution. `Run()` accepts one request; completion comes later through `Result`. For write requests, caller-owned buffers remain pinned until `Free()`. For sendfile responses, `File()` lets the foreign protocol reframe headers/trailers and explicitly call `Context::Send()`.

Dependencies and integration: uses xrootd wire types from `XPtypes.hh`, `XrdLink`, and `XrdSecEntity`. The concrete implementation is `XrdXrootdTransit`.

Risks and test signals: the interface requires callers to be thread-safe and not depend on thread-local state. Tests should cover one-request-at-a-time rejection, buffer lifetime through `Free()`, wait behavior with `SetWait()`, sendfile callback completion, and callback return values that terminate the bridge.
