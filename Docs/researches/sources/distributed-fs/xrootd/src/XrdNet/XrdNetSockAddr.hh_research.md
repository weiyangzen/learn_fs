# sources/distributed-fs/xrootd/src/XrdNet/XrdNetSockAddr.hh

## Purpose
`XrdNetSockAddr.hh` defines `XrdNetSockAddr`, a minimal union for IPv4, IPv6, and generic socket address views.

## Important APIs, Types, and Functions
The union exposes `sockaddr_in6 v6`, `sockaddr_in v4`, and `sockaddr Addr`. There are no functions.

## Control Flow and State
Callers fill one view and read another according to `sa_family`. The union is used to avoid the larger `sockaddr_storage` footprint where only IPv4/IPv6 are needed.

## Dependencies and Integration Points
It includes `<sys/socket.h>` and `<netinet/in.h>`. It is embedded in `XrdNetPeer`, passed through `XrdNetUtils`, and used by socket/refresh/PMark code.

## Risks and Test Signals
Risks are unsupported address families and code assuming `v6.sin6_port` and `v4.sin_port` layout interchangeably. Tests should validate IPv4/IPv6 formatting, comparison, encoding, and port extraction paths.
