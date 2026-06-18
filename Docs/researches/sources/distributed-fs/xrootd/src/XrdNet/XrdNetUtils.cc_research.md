# sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.cc

## Purpose
`XrdNetUtils.cc` implements address comparison, encoding/decoding, host resolution, formatting, protocol/service lookup, network-stack detection, host pattern matching, port parsing, and nonblocking connect-with-timeout helpers.

## Important APIs, Types, and Functions
Major APIs include `Compare()`, `Decode()`, `Encode()`, three `GetAddrs()` overloads, `GetSokInfo()`, `Hosts()`, `IPFormat()`, `Match()`, `MyHostName()`, `NetConfig()`, `Parse()`, `Port()`, `ProtoID()`, `ServPort()`, `SetAuto()`, `Singleton()`, and `ConnectWithTimeout()`. Private `hpSpec`, `FillAddr()`, `GetAInfo()`, `GetHints()`, `GetHostPort()`, `setET()`, and `SetSockBlocking()` provide shared implementation.

## Control Flow
Resolution starts by parsing host/port, choosing addrinfo hints from `AddrOpts`, resolving with `getaddrinfo()`, filtering unsupported/link-local entries, partitioning IPv4/IPv6 or mapped addresses, applying optional rotation, and filling `XrdNetAddr` objects. `%`-prefixed string specs are delegated to `XrdNetRegistry`. Formatting wraps `XrdNetAddr`. `ConnectWithTimeout()` flips a socket nonblocking, calls `connect()`, polls for writability, checks `SO_ERROR`, restores blocking mode, and closes the FD on failure.

## State and Persistence
Static `autoFamily` and `autoHints` capture preferred address-family behavior, initialized from interface inspection. Other state is stack/local. There is no disk persistence.

## Dependencies and Integration Points
The file depends on libc networking APIs, `XrdNetAddr`, `XrdNetIdentity`, `XrdNetIF`, `XrdNetRegistry`, `XrdOucTList`, `XrdOucUtils`, and XrdSys platform/error helpers. It is a common dependency for clients, servers, PMark Firefly, refresh, registry, security, and config parsers.

## Risks and Test Signals
Several details deserve tests: `GetSokInfo()` uses `htons()` where `ntohs()` would normally be expected for extracting a network-order port; `ConnectWithTimeout()` closes the caller's FD on failure, which must match caller expectations; multi-host `GetAddrs()` with `force=true` can silently skip bad entries; address-family ordering and mapped IPv4 behavior are subtle; service-name lookup depends on system databases. Tests should cover IPv4/IPv6/mapped round trips, port parsing modes, registry dispatch, ordering flags, rotation, link-local filtering, `prefAuto`, `Match()` wildcard and `+` expansion, `Singleton()`, connect timeout success/failure, and FD blocking restoration.
