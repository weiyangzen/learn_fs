# sources/test-tools/strace/src/rtnl_netconf.c

Purpose: Decodes network configuration route-netlink messages.

Important APIs/types/functions: `decode_netconfmsg` and `netconfmsg_nla_decoders`.

Control flow: prints family then decodes aligned `NETCONFA_*` attributes as ifindex or signed 32-bit config values.

State and persistence: stateless.

Dependencies/integration: Linux `netconf.h`, route-netlink dispatcher, nlattr helpers, netconf attr xlat.

Risks: table must track new kernel attrs; all current scalar attrs are signed, so type mismatches would affect output.

Test signals: IPv4/IPv6 netconf dumps with forwarding/rp_filter/proxy/input attrs and short headers.
