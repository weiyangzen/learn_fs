## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.cc

Purpose: Implements read-only address formatting, classification, reverse DNS naming, and address equality for `XrdNetAddrInfo`.

Important APIs and functions: `Format`, `isLocal`, `isLoopback`, `isPrivate`, `isRegistered`, `isUsingTLS`, `isHostName`, `Name`, `Port`, `Resolve`, and `Same` are implemented. Private helpers include `LowCase` and `QFill`.

Control flow: `Format` handles Unix, cached hostname, auto/name/address modes, IPv4, IPv6, mapped IPv4, deprecated mapped forms, bracket insertion, and optional port omission. `Name` returns cached or DNS-cache names before calling `Resolve`. `Resolve` uses `getnameinfo`, falls back to numeric formatting, normalizes IPv6 bracket form, and stores successful results in the cache. Classification methods branch on address family and mapped IPv4 handling. `Same` optionally checks port and compares cross-family mapped IPv4 addresses.

State and persistence: Each object owns `hostName` and sockaddr/unix-path storage; `dnsCache` is a static optional process cache. Reverse-lookup results are cached per object and optionally globally.

Dependencies and integration points: Uses system socket/address functions, `XrdNetCache`, and `XrdNetSockAddr`. Consumers use this class when deciding security, routing, logging, message destinations, and local/private/registered status.

Risks: `Format` mutates `hostName` by triggering DNS lookup in name mode, so a read-looking operation can allocate and cache. DNS cache use is global. `isLoopback` uses a compact byte comparison for mapped loopback that depends on structure representation. `Same` may consider differing families equal by hostname if both names exist, which depends on prior resolution. Formatting failure writes question marks and returns zero, so callers must check lengths.

Test signals: Format IPv4, IPv6, mapped IPv4, raw no-port, old mapped form, Unix sockets, small buffers, and hostname modes. Test private/local/loopback classes for RFC1918, link-local, ULA, mapped, and Unix addresses. Validate DNS success/failure cache behavior and `Same` with and without ports.
