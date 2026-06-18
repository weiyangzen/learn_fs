# File Research: sources/os/plan9/9front/sys/src/cmd/ip/snoopy/icmp6.c

This module decodes ICMPv6 and several neighbor-discovery option formats. It supports filtering by type and selecting embedded IPv6 payloads for selected error messages.

`p_seprint` prints type name, code, checksum, and type-specific details for unreachable, packet-too-big, time exceeded, parameter problem, echo, router solicit/advertise, neighbor solicit/advertise, redirect, timestamp, info, and multicast query/report/done messages.

`opt_seprint` walks ICMPv6 options and formats source/target link-layer address, prefix information, redirect, and MTU options. Unknown or malformed options fall through to `dump`.

Checksum verification is present but commented out, likely because ICMPv6 checksum needs IPv6 pseudo-header context. Embedded IPv6 payloads are decoded by setting `m->pr = &ip6`.
