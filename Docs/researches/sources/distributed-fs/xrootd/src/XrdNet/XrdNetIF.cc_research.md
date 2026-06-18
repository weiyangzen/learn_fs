## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.cc

Purpose: Implements interface discovery, advertised interface encoding, public/private IPv4/IPv6 routing selection, and destination construction for XRootD network routing.

Important APIs and functions: `Display`, static `GetIF` overloads, `GetDest`, `InDomain`, `Port`, `PortDefault`, `Routing`, `SetIF`, `SetIFNames`, `SetMsgs`, and `SetRPIPA` are public behavior. Private helpers `GenAddrs`, `GenIF`, `GetDomain`, `IsOkName`, `SetIFPP`, `SetIF64`, and `V4LinkLocal` implement routing tables.

Control flow: `GetIF` enumerates usable non-loopback interfaces with `getifaddrs`, filters configured names, excludes link-local addresses, formats addresses, and tags public/private/interface index metadata. `SetIF` sets the port/routing mode, derives interfaces from source DNS or an explicit list, categorizes each as public/private and v4/v6, then calls `GenIF`. `GenIF` writes compact `ifData` strings into a stack buffer, chooses names versus addresses, fills missing alternate protocol destinations from DNS, copies the compact table to heap storage, and relocates pointers. `SetIF64` fills dual-stack selection slots and mask bits.

State and persistence: Static state includes logger, local domain, configured public/private interface names, global routing mask vector, default routing type, default port, null slot, and private-IP resolution policy. Each instance owns an `ifBuff` heap block plus arrays of pointers into it, a port suffix, selected route, mask, and available interface.

Dependencies and integration points: Uses `XrdNetAddr`, `XrdNetAddrInfo`, `XrdNetIdentity`, `XrdNetUtils`, `XrdOucTList`, `XrdSysError`, `getifaddrs`, and network interface flags. It feeds locate/cms routing and client redirection decisions.

Risks: Static routing and interface-name settings are not thread-safe and are intended for initialization. `GenAddrs(const char*, bool)` contains `if (i > iN)` where `i < iN` was likely intended, so alternate DNS-derived addresses may never be accepted. Compact stack buffer writes rely on size assumptions and macros without explicit bounds checks beyond source formatting. `SetIF` decrements `ifCnt` while filling `netAdr`, making the explicit-list loop hard to reason about. `GetName` inline methods can dereference empty `ifNull` slots if callers skip `HasDest`.

Test signals: Enumerate interfaces with and without `getifaddrs`; filter configured public/private interface names; route under `netLocal`, `netSplit`, and `netCommon`; test public/private IPv4/IPv6 combinations, DNS fallback, explicit interface lists, missing interface warnings, domain membership, port suffix formatting, and small destination buffers.
