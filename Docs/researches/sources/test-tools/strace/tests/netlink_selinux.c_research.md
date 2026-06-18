# sources/test-tools/strace/tests/netlink_selinux.c

Purpose: verifies `NETLINK_SELINUX` message and payload decoding for SELinux enforcement, policy load, and AVC denial notifications.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SELINUX)`, `sendto`, `struct nlmsghdr`, `SELNL_MSG_*`, `struct selnl_msg_setenforce`, `struct selnl_msg_policyload`, `struct selnl_msg_avc`, `TEST_NETLINK_`, and `TEST_NETLINK_OBJECT`.

Control flow: `main` opens a SELinux netlink socket, sends a header-only `SELNL_MSG_SETENFORCE` type test, then sends structured messages for setenforce, policyload, and avc payloads through the netlink test macros.

State and persistence: messages are synthetic and nonblocking; the test does not alter SELinux state.

Dependencies and integration points: relies on Linux `selinux_netlink.h` and strace’s netlink object decoder. It is a compact family-specific decoder test.

Risks and edge cases: SELinux netlink availability and header definitions may differ by system. Decoder risks are mostly message type names and small payload struct field formatting.

Test signals: expected output shows SELinux message names and fields, syscall result formatting, and `+++ exited with 0 +++`.
