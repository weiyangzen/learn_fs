## sources/distributed-fs/xrootd/src/XrdNet/XrdNetIF.hh

Purpose: Declares the interface-routing object that represents available public/private IPv4/IPv6 endpoints and chooses advertised destinations.

Important APIs and types: Defines `ifType`, interface availability bits, `netType`, `Display`, `GetDest`, `GetName`, static `GetIF` overloads, `GetIFType`, `HasDest`, `InDomain`, `Mask`, `Name`, `Port`, `Privatize`, `PortDefault`, `Routing`, `SetIF`, `SetIFNames`, `SetMsgs`, and `SetRPIPA`.

Control flow: Inline helpers select `ifAvail` when callers request `ifAny`, combine private/public bits, append port suffixes, and expose mask data used by routing clients.

State and persistence: Instances store compact interface data pointers, DNS-name flags, owned backing buffer, port suffix, port, route, mask, and available interface. Static config and routing state are shared process-wide. No durable persistence.

Dependencies and integration points: Forward declares `XrdNetAddrInfo`, `XrdOucTList`, `XrdSysError`, and `sockaddr`. Used by identity discovery, locate routing, and redirect destination construction.

Risks: `ifData` uses a flexible-array-like `char iVal[6]` pattern and depends on implementation allocation layout. Copying an `XrdNetIF` would copy pointers into the same backing buffer, but copy operations are not disabled. Inline `GetName` uses `strcpy` and assumes the caller supplies at least 256 bytes.

Test signals: ABI/compile tests for enum values used externally; copy-prevention or copy-safety tests; destination/name access for empty and fully populated interface tables.
