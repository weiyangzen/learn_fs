# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcpv6.c

DHCPv6 client used by IPv6 RA processing when managed configuration is indicated. It binds UDP port 546 on the link-local address, sends Solicit/Request or Renew/Rebind transactions to `ff02::1:2`, and includes client DUID, IA_NA, IA_PD, requested DNS servers, and server id when appropriate.

Responses are checked by transaction id and expected message pair. It handles server/client identifiers, IA_NA addresses, IA_PD delegated prefixes, DNS server options, status codes, prefix/address lifetimes, and computes the lease timeout from T1/preferred lifetimes.
