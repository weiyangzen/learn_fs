# sources/test-tools/strace/bundled/linux/include/uapi/linux/netconf.h

Purpose: defines rtnetlink network configuration message ABI for per-family/per-interface forwarding and neighbor-related settings.

Important APIs/types/functions: `struct netconfmsg` carries the address family. Attributes include `NETCONFA_IFINDEX`, `FORWARDING`, `RP_FILTER`, `MC_FORWARDING`, `PROXY_NEIGH`, `IGNORE_ROUTES_WITH_LINKDOWN`, `INPUT`, `BC_FORWARDING`, and `FORCE_FORWARDING`. Special indexes select all or default configuration.

Control flow: userspace sends netconf get/dump messages and receives settings for a family and interface, or all/default pseudo-interfaces.

State/persistence behavior: the header primarily supports observing kernel network configuration; changes occur through related sysctl/rtnetlink paths and persist in network namespace interface/default state.

Dependencies/integration: depends on Linux netlink and type headers. Integrates with IPv4/IPv6 sysctl-backed forwarding, rp_filter, multicast forwarding, proxy neighbor, and link-down route behavior.

Risks and test signals: special negative ifindex constants must not be formatted as unsigned interface indexes. Tests should cover all attrs, `NETCONFA_ALL`, `IFINDEX_ALL`, `IFINDEX_DEFAULT`, and address-family-specific dumps.
