# sources/test-tools/strace/src/rtnl_link.c

Purpose: Large route-netlink decoder for link messages (`ifinfomsg`) and many nested `IFLA_*` attribute families.

Important APIs/types/functions: `decode_ifinfomsg`; decoders for hardware addresses, 32/64-bit link stats, bridge IDs/options, inet/inet6 config/stats, linkinfo kind/data/xstats, VF info, XDP, AF_SPEC, bridge VLAN/tunnel info, property lists, and proto-down reasons.

Control flow: fixed header decoding prints family, hardware type, ifindex, flags, and change mask, then decodes aligned attributes. Many nested decoders are table-driven. `IFLA_LINKINFO` stores `kind` and `slave_kind` strings in a context so later DATA/XSTATS attributes can dispatch to bridge/tun/can-specific decoders. `IFLA_AF_SPEC` has a special AF_BRIDGE path because bridge payloads do not follow the generic address-family nesting shape.

State and persistence: per-message local context only (`ifla_linkinfo_ctx`); no global state. Several decoders pass the fixed `ifinfomsg` as opaque context for family-aware hardware/AF decoding.

Dependencies/integration: broad Linux networking UAPI (`if_link.h`, `if_bridge.h`, rtnetlink), netlink/nlattr framework, xlat tables for link attrs, bridge, VF, XDP, SNMP stats, device config indices, hardware/address-family names, and generic stat decoders exported to other files.

Risks: high churn with kernel UAPI additions. Variable struct sizes are handled for stats and ifmap; VF GUID alignment is explicitly worked around with packed/aligned union cases. Linkinfo DATA ordering depends on KIND being decoded before DATA in the same nested stream; missing or long kind strings fall back to generic parsing. Several attrs are marked unimplemented or default parser.

Test signals: link get/set/new/del messages with stats32/64, bridge AF_SPEC, inet/inet6 config/stats, XDP, VF info, prop list alt names, bridge/tun linkinfo, CAN xstats, short headers, variable stat sizes, and malformed nested attrs.
