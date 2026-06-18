# sources/test-tools/strace/src/rtnl_route.c

Purpose: Decodes route messages (`rtmsg`) and route attributes, including metrics and multipath nexthops.

Important APIs/types/functions: `decode_rtmsg`, `decode_route_addr`, `decode_rta_metrics`, `decode_rta_multipath`, `decode_rtvia`, and xlat-backed `rt_class`, `rt_proto`, `lwt_encap_type` decoders.

Control flow: prints fixed route header fields, then `RTA_*` attrs. Multipath payloads are iterated as aligned `struct rtnexthop` records with nested route attrs after each header. Address attrs use `rtm_family`, and `RTA_VIA` carries its own family.

State and persistence: stateless; fixed `rtmsg` context is passed to attrs.

Dependencies/integration: Linux routing UAPI, nlattr helpers, xlat tables for route attrs/metrics/protocols/scopes/types/flags/tables, inet address decoders.

Risks: `rtnh_len` controls nested iteration and must be bounded by remaining payload. Multipath arrays and nested attrs have complex bracket formatting. Some attrs such as `RTA_ENCAP` are unimplemented.

Test signals: IPv4/IPv6 route add/del/get, metrics, multipath with multiple nexthops, via/newdst, lwt encap type, malformed `rtnh_len`, and unknown attrs.
