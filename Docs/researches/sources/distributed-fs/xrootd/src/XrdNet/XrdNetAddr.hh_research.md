## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddr.hh

Purpose: Declares `XrdNetAddr`, the mutable address manipulation layer over read-only `XrdNetAddrInfo`.

Important APIs and types: Static `DynDNS`, `IPV4Set`, `SetCache`, `SetDynDNS`, `SetIPV4`, and `SetIPV6` expose process-wide controls. Instance APIs include `Port`, `Register`, multiple `Set` overloads, `SetDialect`, `SetLocation`, `SetTLS`, and convenience constructors from sockets and sockaddrs.

Control flow: The header establishes accepted address formats and the `PortInSpec` sentinel semantics for parsing ports from host specifications.

State and persistence: Mutable address data, hostname, socket fd association, location, TLS flag, and dialect are inherited. Static hints and DNS behavior are private global state implemented in the `.cc` file.

Dependencies and integration points: Includes `XrdNetAddrInfo.hh` and forwards `addrinfo`. It is the common address type passed to `XrdNet`, `XrdNetSocket`, `XrdNetSecurity`, `XrdNetIF`, cache, and utility modules.

Risks: Callers can associate fd values with address objects without ownership transfer, so fd lifetime is external. Static IP mode controls are effectively global and irreversible during normal runtime. `SetDialect` stores a pointer that must remain stable.

Test signals: Header/API tests should compile all constructors and overloads; behavioral tests should assert documented port sentinel behavior and global IPv4/IPv6 mode transitions before network initialization.
