# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/dhcp6leased.h

Shared protocol, configuration, and imsg definitions for `dhcp6leased`.

It defines daemon paths, ports, DHCPv6 constants, option/status codes, limits, lease-file prefixes, DUID/UUID sizing, and OpenBSD enterprise number. It declares packed DHCPv6 wire structs for headers, options, DUID UUID, IA_PD, vendor class, and IA_PREFIX; shared imsg wrapper state; interface/prefix configuration queues; runtime interface info; DHCP packet/request/lease imsg payloads; and the full enum of internal imsg message types.

The header also declares cross-module functions for imsg event handling, config allocation/merge/free, string conversion, engine message names, frontend config lookup/change detection, config printing, config parsing, and lease parsing.
