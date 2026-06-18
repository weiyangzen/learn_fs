# sources/test-tools/strace/tests/netlink_generic.c

Purpose: verifies generic netlink (`NETLINK_GENERIC`) decoding for basic `genlmsghdr` messages and selected generic netlink attributes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_GENERIC)`, `struct genlmsghdr`, `GENL_ID_CTRL`, `TEST_NETLINK_OBJECT_EX_`, `TEST_NETLINK`, `TEST_NLATTR_`, `xasprintf`, `midtail_alloc`, and `CTRL_ATTR_*` constants from `linux/genetlink.h`.

Control flow: the test sends a header for `CTRL_CMD_GETFAMILY`, exercises unknown generic-netlink commands, uses initialized header callbacks for nlattr tests, checks unknown attributes and short/string attribute rendering, then emits an `NLMSG_DONE` test.

State and persistence: all state is synthetic message memory and a temporary generic netlink socket. There is no persistent generic netlink family modification.

Dependencies and integration points: relies on `test_netlink.h` and `test_nlattr.h` macros to construct aligned netlink messages and expected output. It checks strace’s generic netlink control-family xlat behavior.

Risks and edge cases: malformed lengths, unknown attribute ids, abbreviated long strings, and callback consistency between `init_genlmsghdr` and `print_genlmsghdr` are the relevant failure surfaces.

Test signals: output should decode `nlctrl`, generic netlink header fields, `CTRL_ATTR_*` names, raw unknown attributes, and `NLMSG_DONE`, ending with `+++ exited with 0 +++`.
