# sources/test-tools/strace/src/rtnl_cachereport.c

Purpose: Decodes multicast routing cache-report netlink messages for IPv4 and IPv6.

Important APIs/types/functions: decoders for `IPMRA_CREPORT_*` and `IP6MRA_CREPORT_*` attributes, message type xlat helpers, and route decoder entry points.

Control flow: chooses attribute tables by address family/message type and decodes message type, VIF id, source/destination addresses, raw packet payload placeholders, and routing table IDs.

State and persistence: stateless.

Dependencies/integration: Linux mroute/mroute6/rtnetlink headers, netlink attribute helpers, xlat tables for IPMRA/IP6MRA message types and attrs.

Risks: raw packet data is intentionally not decoded; malformed lengths must fall back safely. Family selection determines whether in_addr or in6_addr decoders are used.

Test signals: IPv4 and IPv6 cache report messages with source/destination attrs, table attr, packet payload, and unknown attrs.
