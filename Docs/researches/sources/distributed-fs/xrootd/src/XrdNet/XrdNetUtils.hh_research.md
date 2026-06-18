# sources/distributed-fs/xrootd/src/XrdNet/XrdNetUtils.hh

## Purpose
`XrdNetUtils.hh` declares the central network utility API for address operations, host resolution, formatting, protocol detection, parsing, and timed connects.

## Important APIs, Types, and Functions
It defines `IPComp`, `AddrOpts` with enum operators, port sentinel constants, formatting flags, `NetProt`, and `NetType`. Public static methods cover compare, encode/decode, `GetAddrs()` overloads, socket info, host lists, IP formatting, pattern matching, local FQDN, network configuration, host spec parsing, port/protocol/service lookup, automatic family selection, singleton detection, and `ConnectWithTimeout()`.

## Control Flow and State
All behavior is static. Hidden static fields `autoFamily` and `autoHints` drive `prefAuto` resolution. The header documents port-handling modes, ordering semantics, caller ownership of allocated arrays/lists, and FD sign conventions for local versus peer socket addresses.

## Dependencies and Integration Points
It includes STL types and `XrdOucEnum.hh`, forward-declares `XrdNetAddr`, `XrdOucTList`, and `XrdNetSockAddr`, and is included widely across network, client, server, storage, and config code.

## Risks and Test Signals
The API has many sentinel and ownership contracts. Tests should focus on each documented mode: allocated array deletion, vector clearing on failure, `ordn` semantics, `PortInSpec`/`NoPortRaw`, order flags, onlyUDP service lookup, FD sign behavior, and timeout-connect ownership.
