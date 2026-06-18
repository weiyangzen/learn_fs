## sources/distributed-fs/xrootd/src/XrdNet/XrdNet.cc

Purpose: Implements the high-level XRootD network wrapper for binding TCP/UDP or Unix sockets, accepting inbound peers, creating outbound connections, UDP relay sockets, domain trimming, socket defaults, and optional network security authorization.

Important APIs and functions: `Accept(XrdNetAddr&)`, `Accept(XrdNetPeer&)`, `Bind(int)`, `Bind(char*)`, `Connect(XrdNetAddr&)`, `Connect(XrdNetPeer&)`, `Relay`, `Secure`, `Trim`, `unBind`, and `WSize` are public behavior. Private `do_Accept_TCP` overloads and `do_Accept_UDP` perform actual accept/receive work.

Control flow: Binding closes any previous socket, chooses stream versus datagram mode, opens through `XrdNetSocket`, detaches the fd, records the bound port, and creates a UDP `XrdNetBufferQ` when needed. Accept optionally polls for readiness, then dispatches to TCP accept or UDP receive. TCP accept builds an `XrdNetAddr`, sets socket options, authorizes through `XrdNetSecurity`, optionally reverse-resolves, and either returns the modern address or converts to legacy `XrdNetPeer`. UDP accept allocates a queue buffer, reads a datagram with `recvfrom`, rejects loopback/spoofed or unauthorized senders, optionally duplicates the fd, and attaches the buffer to the peer.

State and persistence: Instance state includes logger, security policy pointer, domain suffix, listening fd, bound port, port type, window/buffer sizes, default options, and UDP buffer queue. No durable persistence; sockets and heap buffers are process-local.

Dependencies and integration points: Depends on `XrdNetAddr`, `XrdNetPeer`, `XrdNetSecurity`, `XrdNetSocket`, `XrdNetUtils`, `XrdSysFD`, `poll`, `accept`, `recvfrom`, and socket option helpers. It is a compatibility bridge between newer address APIs and older peer-based code.

Risks: `Secure` merges ownership semantics into raw pointers and can be misused by callers retaining a pointer. `setDomain` assumes non-null input. `do_Accept_TCP` throttles `EMFILE` messages with a static counter shared across all instances. UDP accept stores received data as a null-terminated string and drops binary datagrams containing embedded nulls for string consumers. `XrdNetBufferQ` allocation is mandatory for UDP, so null allocation would crash if `Bind` succeeds but queue creation fails.

Test signals: Bind TCP/UDP to fixed and ephemeral ports; bind Unix stream/datagram paths; accept with timeout and no timeout; exercise authorization allow/deny; verify reverse lookup and no-lookup modes; test UDP buffer recycle and `XRDNET_NEWFD`; inspect socket options for keepalive, nodelay, linger, close-on-exec, and window size.
