# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksserver.py

Purpose: provides the ntlmrelayx SOCKS server and plugin host. It accepts SOCKS4/SOCKS5 client connections, routes them to protocol-specific relay plugins backed by active relayed sessions, keeps idle relays alive, and exposes a small Flask API listing available relays.

Important APIs and control flow: `SocksRelay` is the abstract plugin base. `SOCKS` registers classes from `socksplugins.SOCKS_RELAYS`, starts `RepeatedTimer(keepAliveTimer)`, a REST API thread, and `activeConnectionsWatcher`. `activeConnectionsWatcher()` consumes successful relay tuples and populates `activeRelays[target][port]` with protocol clients, session data, scheme, `inUse`, and optional `isAdmin`. `SocksRequestHandler.handle()` parses SOCKS requests, validates an active relay, directly proxies DNS port 53, instantiates the right plugin, sends success, calls `initConnection()`, `skipAuthentication()`, sets `inUse`, tunnels, and releases `inUse` in `finally`.

State and persistence: all runtime state is in memory: `activeRelays`, plugin registry, global `activeConnections` queue, timer, REST thread, and watcher thread. No durable storage exists.

Dependencies and integration: depends on `socketserver`, `impacket.structure.Structure`, enum support, protocol plugins, Flask for the API, and relay servers that enqueue successful sessions.

Risks and test signals: `activeRelays` is mutated across handler, timer, and watcher threads without locks. Some SOCKS4 byte/string comparisons are Python-version-sensitive, and REST route duplication exists. Tests should cover SOCKS4/5 parsing, domain/IPv4 requests, relay missing errors, plugin dispatch, DNS passthrough, in-use release after exceptions, keepalive removal, active connection registration, and REST relay listing.
