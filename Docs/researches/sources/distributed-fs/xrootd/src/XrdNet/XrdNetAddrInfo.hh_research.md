## sources/distributed-fs/xrootd/src/XrdNet/XrdNetAddrInfo.hh

Purpose: Declares the read-only network address information object used across XrdNet APIs.

Important APIs and types: Defines formatting modes `fmtAuto`, `fmtName`, `fmtAddr`, `fmtAdv6`; options `noPort`, `noPortRaw`, `old6Map4`, `prefipv4`; address type enum `IPType`; `LocInfo`; and accessors/classifiers for family, protocol, socket address, sock size, fd, port, name, TLS, locality, privacy, mapped IPv4, registration, and equality.

Control flow: The header provides inline accessors and an assignment operator that deep-copies hostname and Unix sockaddr state while preserving value semantics for the socket address union.

State and persistence: Owns `XrdNetSockAddr IP`, optional `hostName`, optional Unix-path sockaddr, location metadata, address size, protocol type/flags, associated fd number, and protocol dialect pointer. Static `dnsCache` is shared by all instances.

Dependencies and integration points: Includes socket headers, `XrdNetSockAddr.hh`, and platform definitions. It is the base type for mutable `XrdNetAddr` and is passed to interface, security, PMark, and messaging code when mutation should not be allowed.

Risks: Copy assignment sets `sockAddr` only in some branches; value semantics depend on careful union pointer relocation. `SockFD` maps zero to no fd, so fd 0 cannot be represented as an associated socket. `Dialect` and location fields are not synchronized. `Longtitude` is misspelled in the public struct and must remain ABI-compatible.

Test signals: Copy/assign IPv4, IPv6, Unix, hostname-bearing, and TLS/dialect/location-bearing objects; verify destructors free exactly owned memory; assert fd 0 behavior if callers can pass it.
