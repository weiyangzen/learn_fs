# sources/test-tools/strace/tests/nlattr_ifinfomsg.c

Purpose: provides broad nlattr coverage for interface info (`struct ifinfomsg`) route messages, including link names, MTUs, qdisc/ifalias strings, link stats, maps, proto-down reason arrays, nested AF-specific attributes, and many numeric/flag attributes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifinfomsg`, `IFLA_*`, `struct rtnl_link_stats`, `struct rtnl_link_stats64`, `struct rtnl_link_ifmap`, `TEST_NLATTR_`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT`, `TEST_NLATTR_OBJECT_MINSZ`, `TEST_NESTED_NLATTR_OBJECT_EX_`, and helpers from included `nlattr_ifla.h`/`nlattr_ifla_af_inet6.h`.

Control flow: initializes an ifinfo header and systematically sends attributes of varying primitive/object/string/nested forms. It covers exact objects, minimum-size objects, raw pointer fallbacks, long strings, byte arrays, nested attributes, and loops over repeated proto-down reason values.

State and persistence: no link state is changed. All interface data is synthetic, with loopback ifindex used where symbolic output is expected.

Dependencies and integration points: depends on `linux/if_link.h`, route netlink attribute xlat tables, `test_nlattr.h`, and local headers that factor nested IFLA/AF_INET6 cases.

Risks and edge cases: this is a high-risk decoder surface because attribute coverage spans many kernel versions. Object size evolution, nested attribute alignment, long string truncation, and bitmask formatting can all break expectations.

Test signals: expected output should decode numerous `IFLA_*` attributes, structured link stats/maps, nested AF_SPEC/INET6 objects, unknown/fallback values, and the normal exit line.
