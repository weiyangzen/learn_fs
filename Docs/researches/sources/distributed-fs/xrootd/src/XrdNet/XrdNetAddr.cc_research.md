## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.cc

Purpose: Implements mutable address construction and process-wide DNS/IP mode controls for `XrdNetAddr`, the write-enabled subclass of `XrdNetAddrInfo`.

Important APIs and functions: Constructors, `Hints`, `OnlyIPV4`, `Map64`, `Port`, `Register`, multiple `Set` overloads, `SetCache`, `SetDynDNS`, `SetIPV4`, `SetIPV6`, `SetLocation`, and `SetTLS` are implemented here.

Control flow: Static initialization builds `addrinfo` hints and probes IPv6 support. `Set(const char*, int)` clears prior state, handles wildcard, Unix paths, bracketed IPv6, IPv4, hostnames, and embedded ports, then writes the port. The multi-address `Set` parses host/port, calls `getaddrinfo`, and fills an array while suppressing adjacent duplicates. Sockaddr and fd overloads copy addresses from system calls. Global mode setters mutate shared hint structures and inform `XrdNetUtils`.

State and persistence: Per-object state inherited from `XrdNetAddrInfo` is reset and rewritten on each `Set`. Static state includes hint structures, `useIPV4`, `dynDNS`, and the shared DNS cache pointer. No disk persistence.

Dependencies and integration points: Uses `getaddrinfo`, `inet_pton`, `getsockname`, `getpeername`, `XrdNetIdentity`, `XrdNetUtils`, `XrdNetCache`, and `XrdSysE2T`. It underpins socket bind/connect, interface routing, address comparison, and security checks.

Risks: Static hint mutation is not synchronized and should only happen during initialization. `Set(const sockaddr*)` assumes non-null valid sockaddr. Hostnames containing colon are treated as host:port and may not support all IPv6-literal edge cases unless bracketed. `Register` trusts DNS resolution to validate a supplied hostname and is explicitly not MT-safe. `OnlyIPV4` changes global behavior at static initialization based on one socket probe.

Test signals: Parse wildcard, IPv4, bracketed IPv6, mapped IPv4, Unix paths, hostnames with numeric/service ports, missing ports, invalid ports, and too-long names. Verify IPv4-only and IPv6 mode behavior, dynamic DNS error text, fd peer/local address extraction, hostname registration, and multi-address duplicate suppression.
