# sources/test-tools/strace/src/rtnl_addrlabel.c

Purpose: Decodes route-netlink address-label messages.

Important APIs/types/functions: `decode_ifaddrlblmsg`, `decode_ifal_address`, and `ifaddrlblmsg_nla_decoders`.

Control flow: decodes the fixed `ifaddrlblmsg` header, then aligned `IFAL_*` attributes. Address payloads use `ifal_family` from the header.

State and persistence: stateless.

Dependencies/integration: Linux `if_addrlabel.h`, netlink route/nlattr helpers, addrfam xlat, and rtnl address-label attrs.

Risks: only complete headers enable attribute decode; short messages must not over-read. Attribute table is small, so unknown attrs fall to generic parser.

Test signals: IPv6 addrlabel list/add/delete messages, label attr, malformed short payloads.
