# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiRRAgent.hh

Purpose: declares a privileged helper class that bridges private state between `XrdSsiRequest`, `XrdSsiResponder`, and transport-specific implementations. It avoids exposing lifecycle internals as public API.

Important APIs/types: static methods forward alerts, cleanup, disposal, and accessors for request error/response state. `isaRetry()` tests and optionally clears retry flags. `onServer()` marks a request as server-side. `Request()` gets the responder's bound request. `SetNode()`, `ResetResponder()`, and `SetMutex()` mutate endpoint, responder binding, and request mutex.

Control flow and state: all methods are inline and operate on private fields by friendship. `ResetResponder()` locks the responder mutex before clearing `reqP`. There is no owned state or persistence.

Dependencies and integration: used by lower-level request/session/client code that must coordinate responder binding and request reuse. Risks include misspelled forward declaration `XrdSsiMuex`, bypassing normal invariants, and potential misuse that clears responder/request links without completing lifecycle. Test signals should focus on flows that depend on these helpers: request cleanup before reuse, retry flag one-shot behavior, server/client `ProcessResponse` branch selection, and responder reset under lock.
