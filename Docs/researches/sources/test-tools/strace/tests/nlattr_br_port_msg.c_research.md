# sources/test-tools/strace/tests/nlattr_br_port_msg.c

Purpose: tests route-netlink attributes attached to `struct br_port_msg` multicast database messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct br_port_msg`, `RTM_NEWMDB`/bridge rtnetlink constants, `TEST_NLATTR_`, `test_nlattr.h`, and `ifindex_lo`.

Control flow: initializes and prints a bridge port message header, then sends one or more attributes through the nlattr macro framework to verify attribute names and payload formatting.

State and persistence: no bridge or multicast database state is changed; data is synthetic.

Dependencies and integration points: depends on `linux/if_bridge.h`, `linux/rtnetlink.h`, and the strace route nlattr decoder.

Risks and edge cases: bridge attribute constants and interface-index symbolic rendering can vary with headers/environment.

Test signals: expected output shows a route netlink message with decoded `br_port_msg` header and bridge-specific attributes.
