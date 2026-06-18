# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcp6d.c

Minimal stateless DHCPv6 server for network boot. It listens on `dhcp6s`, joins `ff02::1:2` on link-local IPv6 interfaces, parses client/server ID and option-request TLVs, and replies to Solicit, Request, and Information-request messages.

Client identity is derived from DUID client ID when possible, otherwise from EUI-64-like link-local IPv6 address bytes. Address and option data are looked up in ndb using Ethernet address, target IPv6 records, interface networks, and requested attributes.

Supported responses include server ID, client ID, IA_NA with infinite preferred/valid lifetimes for ndb IPv6 addresses, DNS servers, DNS domain list, and bootfile URL assembled from `bootf`/`tftp`.
