# sources/test-tools/strace/tests/netlink_xfrm.c

Purpose: verifies `NETLINK_XFRM` message type and flag decoding for IPsec/XFRM netlink operations.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_XFRM)`, `sendto`, `struct nlmsghdr`, `XFRM_MSG_NEWSA`, `XFRM_MSG_GETSA`, `XFRM_MSG_DELSA`, `XFRM_MSG_ALLOCSPI`, and `NLM_F_*` flags.

Control flow: `main` opens an XFRM netlink socket, sends one header for type decoding, then sends multiple headers combining XFRM message types with dump/create/delete-style flags to verify symbolic flag rendering.

State and persistence: sends only header-only nonblocking test messages and does not change XFRM state or security associations.

Dependencies and integration points: depends on Linux `xfrm.h` constants and strace’s netlink protocol/type xlat tables.

Risks and edge cases: flag interpretation depends on message type context; changes in XFRM constants or decoder-specific flag sets can affect expected strings.

Test signals: output should show symbolic XFRM message names, context-sensitive `NLM_F_*` combinations, syscall result strings, and normal exit.
