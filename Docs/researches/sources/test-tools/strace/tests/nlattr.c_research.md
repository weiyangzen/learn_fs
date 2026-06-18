# sources/test-tools/strace/tests/nlattr.c

Purpose: stress-tests generic netlink attribute parsing and rendering with UNIX diag messages, including malformed lengths, nesting, arrays, abbreviated strings, and unknown attribute types.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_SOCK_DIAG)`, `sendto`, `struct nlmsghdr`, `struct unix_diag_msg`, `struct nlattr`, `NLA_F_NESTED`, `UNIX_DIAG_*`, `DEFAULT_STRLEN`, `print_quoted_hex`, and helper-constructed message buffers.

Control flow: builds netlink messages containing UNIX diag payloads and attributes, then sends sequences with too-short attributes, exact attributes, nested attributes, arrays, unknown ids, long string payloads, and trailing data. Each send is paired with hand-written expected output.

State and persistence: all state is synthetic buffers and one sock_diag netlink fd. No real socket diagnostics are queried or persisted.

Dependencies and integration points: validates the low-level nlattr decoder that many protocol-specific tests depend on. Uses Linux rtnetlink/sock_diag/unix_diag headers for constants and structure sizes.

Risks and edge cases: attribute length arithmetic, alignment padding, nested array delimiters, default string abbreviation, and unknown type rendering are the main fragile points.

Test signals: expected trace shows structured attributes where valid, raw pointers/hex for malformed data, abbreviation markers, and a final `+++ exited with 0 +++`.
