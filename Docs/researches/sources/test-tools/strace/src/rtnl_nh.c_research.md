# sources/test-tools/strace/src/rtnl_nh.c

Purpose: Decodes nexthop route-netlink messages and resilient group/bucket attrs.

Important APIs/types/functions: `decode_nhmsg`, `decode_nha_nh_grp`, `decode_nha_addr`, resilient group/bucket decoders, and `print_nh_grp`.

Control flow: fixed `nhmsg` prints family/scope/protocol/flags, then attrs. Group attrs are arrays of `struct nexthop_grp`; gateway/address attrs use `nh_family`; resilient attrs decode nested groups and buckets with clock/scalar fields.

State and persistence: stateless; fixed header is passed as opaque context for family-aware address decoding.

Dependencies/integration: Linux nexthop/rtnetlink UAPI, nlattr helpers, xlat tables for nexthop attrs and group types, route scope/protocol flags.

Risks: group arrays require exact element-size division; resilient attr support depends on newer kernel headers. Unknown nested attrs must remain generic.

Test signals: single nexthop, group nexthop, resilient groups/buckets, IPv4/IPv6 gateways, malformed group payload lengths.
