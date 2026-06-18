# sources/test-tools/strace/src/rtnl_addr.c

Purpose: Decodes route-netlink address messages (`ifaddrmsg`) and their attributes.

Important APIs/types/functions: `decode_ifaddrmsg`, `decode_ifa_address`, `decode_ifa_cacheinfo`, `decode_ifa_flags`, and `ifaddrmsg_nla_decoders`.

Control flow: prints fixed `ifaddrmsg` fields after fetching all but the already-known family byte. If the fixed header is complete, it decodes aligned `IFA_*` attributes, using the message family to decode address payloads.

State and persistence: stateless; passes the decoded header as opaque context for address attribute decoding.

Dependencies/integration: `netlink_route.h`, `nlattr.h`, Linux `if_addr.h`, xlat tables for flags/scopes/attrs, and inet address decoders.

Risks: short messages must show more-data rather than reading past bounds. Address attributes depend on `ifa_family`; bad family values should still preserve raw output.

Test signals: IPv4/IPv6 address add/delete/get messages, cacheinfo, flags attr, target netns id, short headers, and malformed attrs.
