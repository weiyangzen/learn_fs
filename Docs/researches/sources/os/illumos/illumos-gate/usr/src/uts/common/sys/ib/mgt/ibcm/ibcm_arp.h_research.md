# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/mgt/ibcm/ibcm_arp.h

## Scope

Defines private IBCM ARP/IP-to-InfiniBand address resolution data structures and prototypes.

## APIs And Structures

- `IBCM_ARP_MAX_IFNAME_LEN` caps interface names at 24 bytes.
- `IBCM_H2N_GID(gid)` converts the two 64-bit halves of an `ib_gid_t` from host to network ordering using 32-bit `ntohl()` pieces.
- Path-record wait queue flags:
  - `IBCM_ARP_PR_RT_PENDING`
  - `IBCM_ARP_PR_RESOLVE_PENDING`
- `ibcm_arp_prwqn_t` tracks an address-resolution wait node, including stream state, user/source/destination/gateway/netmask IP addresses, interface name/protocol, IPoIB source/destination MACs, source/destination GIDs, and `ip2mac_id_t`.
- `ibcm_arp_streams_t` provides a mutex, condition variable, status, done flag, and current wait queue node.
- `ibcm_arp_ip_t` represents an IP-over-IB interface instance with datalink ID, P_Key, HCA GUID, port GID, address family, IPv4/IPv6 socket address, and zone ID.
- `ibcm_arp_ibd_insts_t` stores an allocated array of IPoIB instances.

## Functions

- `ibcm_arp_get_ibaddr()` resolves source/destination IP addresses to source/destination IB GIDs and returns the resolved source IP.
- `ibcm_arp_get_ibds()` discovers IPoIB instances for an address family.
- `ibcm_arp_free_ibds()` releases instance arrays returned by discovery.

## Dependencies

- Includes `ibcm_impl.h`, IPoIB client definitions, `inet/ip2mac.h`, and IPv6 definitions.
- Bridges IBCM connection setup with IP routing, ARP/neighbor resolution, IPoIB MAC addresses, zones, and datalinks.

## Risks And Invariants

- `IBCM_H2N_GID` mutates its argument and assumes the GID halves can be addressed as two 32-bit words.
- Resolution state is synchronized through `ibcm_arp_streams_t` mutex/CV and must keep the wait node valid while asynchronous routing or IP-to-MAC resolution is pending.
- Zone, family, P_Key, and HCA/port GID must match the intended IPoIB interface, or path records may be built for the wrong fabric endpoint.
