## sources/sync-backup/syncthing/lib/osutil/net.go

Purpose: helpers for interface address enumeration and IP extraction from strings or `net.Addr`.

Important APIs: `GetInterfaceAddrs(includePtP)` returns IP networks for up interfaces while excluding loopback and, by default, point-to-point interfaces. `IPFromString` parses host:port or raw host strings. `IPFromAddr` extracts IPs from `*net.TCPAddr`, `*net.UDPAddr`, `*net.IPAddr`, and `*net.IPNet`.

Control flow and state: `GetInterfaceAddrs` obtains interfaces through `netutil.Interfaces`, filters flags, obtains addresses via `netutil.InterfaceAddrsByInterface`, extracts IPs, and appends only valid `*net.IPNet` addresses. `IPFromString` first tries `net.SplitHostPort`, then raw parse. `IPFromAddr` switches on address type and returns an error for unsupported types.

Dependencies and integration points: used by NAT mapping gateway validation and address/listener selection. Android behavior depends on `netutil` wrappers.

Risks: interface filtering can omit useful point-to-point addresses unless requested. Unsupported address types return errors. Host parsing can treat malformed host:port strings as raw IP parse failures.

Test signals: `osutil_test.go` covers `IPFromString`; other functions are indirectly covered.
