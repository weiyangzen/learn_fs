# sources/test-tools/strace/tests/nlattr_ifaddrlblmsg.c

Purpose: tests route-netlink attributes attached to interface address-label messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifaddrlblmsg`, `IFAL_*`, `RTM_NEWADDRLABEL`, `TEST_NLATTR_`, `TEST_NLATTR`, and `ifindex_lo`.

Control flow: initializes an address label header and sends attributes such as address and label values through the nlattr test macros.

State and persistence: no address labels are configured; messages are synthetic.

Dependencies and integration points: depends on `linux/if_addrlabel.h`, route netlink constants, and strace route nlattr decoding.

Risks and edge cases: attribute payload sizes and ifindex rendering are the likely regressions.

Test signals: expected trace decodes the `ifaddrlblmsg` header and `IFAL_*` attributes.
