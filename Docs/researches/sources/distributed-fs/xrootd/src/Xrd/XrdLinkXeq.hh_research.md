## sources/distributed-fs/xrootd/src/Xrd/XrdLinkXeq.hh

Purpose: declares the protected implementation behind `XrdLink`. It inherits from `XrdLink` and exposes executor operations to `XrdLinkCtl` while keeping protocol-facing callers on the facade.

Important APIs/types/functions: public executor methods mirror link operations plus TLS-specific methods. Public members `LinkInfo` and `PollInfo` are the embedded lifecycle and poll state. Protected helpers include `RecvIOV`, `sendData`, `SendIOV`, `SFError`, `TLS_Error`, and `TLS_Write`. Static counters back link XML stats.

Control flow: `XrdLinkCtl` allocates concrete `XrdLinkXeq`/`XrdLinkCtl` objects, `XrdLink` delegates to these methods, and pollers schedule the inherited job interface.

State/persistence: stores protocol pointers (`Protocol`, `ProtoAlt`), close callback, TLS socket, network address, read/write mutexes, optional `sendQ`, host length, read-lock/fd-keep flags, idle marker, and fixed username/link-name buffers. No durable persistence.

Dependencies/integration: includes `XrdLink`, `XrdLinkInfo`, `XrdPollInfo`, `XrdProtocol`, `XrdNetAddr`, `XrdTls`, and `XrdTlsSocket`.

Risks: `Uname` and `Lname` adjacency is documented as required for client name formatting; layout changes could break `Client()`. The destructor is intentionally unused, so member resources must be reset/recycled manually. Exposing `LinkInfo` and `PollInfo` publicly makes invariants dependent on cooperating classes.

Test signals: ABI-sensitive tests should cover `Client()` formatting, link reset, protocol push/pop behavior, TLS version reporting, and close callback registration only for the active protocol.
