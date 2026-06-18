# sources/test-tools/strace/src/rtnl_mdb.c

Purpose: Decodes bridge multicast database route-netlink messages.

Important APIs/types/functions: `decode_br_port_msg`, `decode_mdba_mdb_entry_info`, `decode_mdba_router_port`, and nested MDB/router decoder tables.

Control flow: fixed `br_port_msg` prints family and ifindex, then `MDBA_*` attrs. MDB entries decode `br_mdb_entry`, flags/state/vid, protocol/address union, and optional extended attrs. Router ports decode ifindex and optional timer/type nested attrs.

State and persistence: stateless.

Dependencies/integration: Linux bridge UAPI, netlink helpers, xlat tables for MDB attrs, states, flags, multicast router types, and address-family printers.

Risks: comment notes ABI ambiguity/breakage around flags/vid presence on some architectures. Address decoding depends on embedded protocol. Nested payloads can contain aligned data after fixed structs.

Test signals: MDB entries for IPv4/IPv6, router port attrs, timers, flags/vid fields, short payloads, and malformed nested attrs.
