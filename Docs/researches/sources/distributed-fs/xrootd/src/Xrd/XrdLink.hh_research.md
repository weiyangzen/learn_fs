## sources/distributed-fs/xrootd/src/Xrd/XrdLink.hh

Purpose: declares the public connection object for XRootD protocol code. `XrdLink` inherits `XrdJob` so links can be scheduled, but it presents a connection-centric API for address identity, I/O, TLS, protocol binding, statistics, and administrative termination.

Important APIs/types/functions: exported methods include `Activate`, `Close`, `Enable`, `Find`, `getName`, `Recv`, `RecvAll`, `Send`, `Serialize`, `setID`, `setProtocol`, `setTLS`, `Shutdown`, `Stats`, `Terminate`, and identity accessors such as `Host`, `Name`, `NetAddr`, `FDnum`, `Inst`, `UseCnt`, and `hasTLS`. `sfVec` aliases `XrdOucSFVec` for sendfile vectors, and static `sfOK` advertises sendfile support.

Control flow: callers receive `XrdLink*` from network accept or link lookup, then interact with it through this facade. Protocols call `Recv`/`Send` during `Process()`, may upgrade with `setTLS()`, can switch protocol objects with `setProtocol()`, and can close or terminate links. Static scans route to `XrdLinkCtl`.

State/persistence: exposes public `ID` for fast protocol/log access and stores protected identity/lifecycle fields `HostName`, `Instance`, `isBridged`, and `isTLS`. Persistent storage is absent; link objects are reused in memory and `ResetLink()` prepares them for new connections.

Dependencies/integration: includes network address types, scheduler job base class, sendfile vector support, pthread wrappers, `XrdLinkXeq`, `XrdPollInfo`, `XrdProtocol`, and TLS types.

Risks: the public `ID` pointer is intentionally mutable legacy state and must remain valid across protocol logging. The destructor is protected and link objects are "never deleted", so allocation/reuse invariants in `XrdLinkCtl` are essential. API comments define blocking behavior; incorrect timeout expectations can deadlock protocol code.

Test signals: compile-time consumers should cover raw I/O, vectored I/O, sendfile gated by `sfOK`, TLS upgrade/downgrade, static link iteration, and protocol replacement with `push=true`.
