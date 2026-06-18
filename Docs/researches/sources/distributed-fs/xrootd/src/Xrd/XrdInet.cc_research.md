<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc -->
# sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc

Purpose: implements `XrdInet`, a server/client TCP network wrapper over `XrdNet` that returns `XrdLink` objects, supports optional security authorization, systemd socket activation, scalable accept/connect behavior, and listener setup.

Important APIs/types/functions: static `AssumeV4`, `TraceID`, `netIF`, methods `Accept`, `BindSD`, `Connect`, private `Listen`, and `Secure`.

Control flow: `Accept()` loops on `XrdNet::Accept()` until success unless a timeout is specified, posts an optional semaphore after accept, optionally resolves the peer name, checks `XrdNetSecurity::Authorize`, closes unauthorized sockets, and wraps accepted sockets via `XrdLinkCtl::Alloc`. `BindSD()` uses systemd-provided sockets when available and matching requested port/type; otherwise it falls back to `Bind()`. For stream sockets it calls `Listen()`. `Connect()` opens an outbound connection and wraps it in `XrdLink`. `Secure()` merges or installs security policy.

State and persistence behavior: instance state is the inherited bound socket and `Patrol` pointer; class state holds interface routing object and IPv4 assumption flag. Runtime side effects include accepted/connected sockets, closed unauthorized sockets, systemd fd adoption, UDP buffer queues in inherited state, and trace/log messages.

Dependencies: `XrdNet`, `XrdNetAddr`, `XrdNetOpts`, `XrdNetSecurity`, `XrdLinkCtl`, `XrdTrace`, optional systemd `sd-daemon`, optional `XrdNetBuffer`/`XrdNetSocket`, POSIX sockets, DNS/name lookup, and logging.

Integration points: created by `XrdConfig::getNet()` for listening ports and exposed through `XrdProtocol_Config::NetTCP`. Accepted sockets become `XrdLink` instances managed by link control and protocol dispatch. `XrdConfig::xallow` supplies `Patrol`; `xnet` configures routing/name behavior through shared network/interface classes.

Risks: the accept loop sleeps and logs every 60 failures for non-timeout accepts, so persistent accept errors can delay shutdown/error handling. Authorization may require name resolution if reverse lookup is enabled, affecting latency. Systemd socket matching must align with port, address family, and stream/datagram type. `unkown.endpoint` typo is harmless but visible in logs.

Test signals: accept/connect smoke tests, authorization allow/deny tests, timeout accept behavior, systemd socket activation tests when built with `HAVE_SYSTEMD`, listen backlog error tests, DNS/no-reverse-lookup tests, and trace/log assertions for accepted/connected links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/Xrd/XrdInet.cc -->
