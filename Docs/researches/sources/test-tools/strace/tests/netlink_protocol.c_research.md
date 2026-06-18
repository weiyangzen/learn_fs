# sources/test-tools/strace/tests/netlink_protocol.c

Purpose: stress-tests generic netlink message framing and protocol-level decoding independent of a specific family, including null buffers, short buffers, multi-message arrays, `NLMSG_ERROR`, and `NLMSG_DONE`.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `struct nlmsghdr`, `NLMSG_NOOP`, `NLMSG_ERROR`, `NLMSG_DONE`, `struct nlmsgerr`, `NLMSG_HDRLEN`, tail/midtail allocation, `print_quoted_hex`, and `sprintrc`.

Control flow: the test sends null and zero-length buffers, EFAULT pointers, too-short byte strings, single and multiple aligned netlink messages, intentionally truncated multi-message sequences, many `NLMSG_ERROR` payload variants with nested original headers, and `NLMSG_DONE` payload variants.

State and persistence: uses only a temporary netlink socket and synthetic buffers. It does not rely on kernel message semantics because malformed buffers are expected.

Dependencies and integration points: validates strace’s generic netlink parser before family-specific dispatch. It integrates with allocation helpers that place buffers near inaccessible memory to exercise pointer fault handling.

Risks and edge cases: length arithmetic, alignment, nested error message decoding, EFAULT display, empty payload rendering, and multi-message array boundaries are all fragile and explicitly covered.

Test signals: expected output should distinguish `NULL`, empty strings, raw byte strings, arrays of messages, truncated `...`, structured errors/done values, unknown flags, and normal exit.
