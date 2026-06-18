## sources/distributed-fs/xrootd/src/Xrd/XrdLink.cc

Purpose: implements the public `XrdLink` facade used by protocols and pollers to operate a client connection without exposing the full `XrdLinkXeq` implementation. Most methods are small delegates, but this file owns TLS/non-TLS dispatch, reference-count coordination, link serialization, termination arbitration, and low-level readiness checks.

Important APIs/types/functions: `Activate()` attaches `linkXQ.PollInfo` to `XrdPoll`; `Recv`, `RecvAll`, `Peek`, and `Send` select TLS or raw executor methods based on `isTLS`; `setProtocol()` installs a protocol and optionally invokes `DoIt()`; `Serialize()` waits for `InUse <= 1`; `setRef()` updates `XrdLinkInfo::InUse` and releases serialization waiters; `Terminate()` implements owner-checked remote termination; `Stats()` delegates to `XrdLinkXeq::Stats`.

Control flow: accepted links are allocated by `XrdLinkCtl`, assigned a protocol by `XrdProtLoad` or the main acceptor, then `Activate()` places them into a poller. Poll callbacks run the protocol through `DoIt()` in `XrdLinkXeq`; public reads and writes return through this facade. Termination first resolves a target fd/instance, checks owner and host identity, then runs in the target link context to disable polling and wait for close notification.

State/persistence: no durable persistence. Runtime state is held in `HostName`, `Instance`, `isBridged`, `isTLS`, `ID`, and executor-owned `LinkInfo`/statistics. `ResetLink()` frees the host name and clears transient flags before fd reuse.

Dependencies/integration: depends on `XrdLinkXeq`, `XrdLinkCtl`, `XrdPoll`, `XrdProtocol`, `XrdTlsContext`, `XrdTlsPeerCerts`, and global logging/tracing. It is the stable API consumed by protocol implementations.

Risks: `setRef()` repairs zero or negative use counts after logging, which can hide upstream lifecycle bugs. `Terminate()` relies on caller-supplied `owner`, `ID`, host comparison, fd, and instance checks; regressions here could kill the wrong reused fd. `Wait4Data()` and raw `Peek()` must not be used incorrectly on TLS links.

Test signals: exercise protocol processing over TLS and non-TLS links, fd reuse with mismatched `Instance`, owner-denied termination, deferred close with active users, and XML link stats after `syncStats()`.
