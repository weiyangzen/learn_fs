# sources/test-tools/strace/tests/netlink_nlctrl.c

Purpose: deeply tests generic netlink control-family (`nlctrl`) decoding, including command headers, primitive attributes, nested operations, multicast groups, policy descriptions, operation policies, and known family-specific command tables.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_GENERIC)`, `struct genlmsghdr`, `GENL_ID_CTRL`, `CTRL_CMD_*`, `CTRL_ATTR_*`, `NL_POLICY_TYPE_ATTR_*`, `TEST_NETLINK_OBJECT_EX_`, `TEST_NLATTR`, `TEST_NLATTR_`, `TEST_NLATTR_EX_`, `check_x16_nlattr`, `check_u32_nlattr`, `xasprintf`, and xlat constants for devlink, ethtool, ioam6, mptcp, netdev, nl80211, seg6, taskstats, tcp_metrics, and thermal.

Control flow: `main` creates a generic netlink socket and shared message buffer, then runs header decoding for all control commands, unknown/x16/u32/string attributes, nested `CTRL_ATTR_OPS`, nested multicast groups, nested policy entries with 64-bit and 32-bit bounds, operation policy arrays, family-specific operation tables, and `NLMSG_DONE`.

State and persistence: all state is synthetic aligned `nlattr` trees in stack or tail-allocated buffers. The test performs no real control-family queries or family registration changes.

Dependencies and integration points: heavily integrates with `test_netlink.h`, `test_nlattr.h`, xlat tables, and many Linux generic netlink UAPI headers. It is a high-value regression test for nested nlattr rendering.

Risks and edge cases: nested attribute array formatting, xlat availability across kernel header versions, attribute alignment, unknown command fallback, and long generated expected strings are the main maintenance risks.

Test signals: output must decode `nlctrl` headers, primitive and nested attributes, policy type names and values, known family command names, unknown command comments, `NLMSG_DONE`, and the exit marker.
