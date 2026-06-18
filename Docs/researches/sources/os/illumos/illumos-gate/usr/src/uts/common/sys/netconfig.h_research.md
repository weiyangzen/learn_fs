# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/netconfig.h

Network selection/configuration database ABI header for `/etc/netconfig`.

Key responsibilities:
- Defines `NETCONFIG` path and `NETPATH` environment variable name.
- Defines `struct netconfig` entries with network ID, semantics, flags, protocol family, protocol, device, lookup-library list, and reserved fields.
- Defines iteration handle `NCONF_HANDLE`.
- Defines transport semantics values for connectionless, connection-oriented, orderly release, raw, and private RDMA.
- Defines flags for visible and broadcast networks.
- Defines protocol family strings, including loopback, inet, inet6, many legacy families, and private RDMA.
- Defines protocol strings for tcp, udp, icmp, and RDMA provider names.
- Declares netconfig/netpath iteration, lookup, free, and error-reporting APIs.

Dependencies:
- Standalone public C/C++ header.

Notable risks:
- RDMA semantics and family values are explicitly private Solaris kRPC interfaces despite being present in a public-looking header.
- Reserved fields are noted as borrowed by services such as lockd, so ABI consumers may depend on them.
