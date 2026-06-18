# sources/test-tools/strace/tests/nlattr_dcbmsg.c

Purpose: tests attributes on rtnetlink DCB (`struct dcbmsg`) messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct dcbmsg`, `RTM_GETDCB`/DCB command constants, `TEST_NLATTR_`, and `test_nlattr.h`.

Control flow: initializes and prints a DCB message header, then uses the nlattr framework to send DCB attributes with expected decoded names and payloads.

State and persistence: no DCB configuration is queried or changed; messages are synthetic.

Dependencies and integration points: depends on `linux/dcbnl.h`, `linux/rtnetlink.h`, and the route nlattr decoder.

Risks and edge cases: DCB command and attribute constants can differ by header version. Short payload handling is covered by helper macros.

Test signals: expected trace includes decoded DCB header fields and DCB attribute output.
