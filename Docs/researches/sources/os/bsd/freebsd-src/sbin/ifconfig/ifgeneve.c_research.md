# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifgeneve.c

`ifgeneve.c` implements GENEVE interface support for netlink-enabled `ifconfig` builds. It registers clone creation for `geneve*` interfaces, GENEVE-specific configuration commands, GENEVE status output, and parser verification for nested netlink attributes.

Status fetches `RTM_GETLINK` data for a GENEVE interface, parses nested `IFLA_LINKINFO`/`IFLA_INFO_DATA`, prints mode (`l2` or `l3`), VNI, local/remote or multicast group endpoint, device for multicast, and in verbose mode prints port range, TTL, DSCP inheritance, DF behavior, external metadata mode, L2 forwarding-table state/counters, and offload statistics.

Configuration commands send `RTM_NEWLINK` messages with nested GENEVE attributes. They set clone-time mode, VNI, local address, remote address, multicast group, local/remote ports, source port range, forwarding-table timeout/max entries, multicast device, TTL or inherit, DF mode, DSCP inheritance, learning, flush behavior, external metadata mode, and GENEVE hardware checksum/TSO capabilities. Address validation distinguishes multicast-only group addresses from non-multicast local/remote endpoints.
