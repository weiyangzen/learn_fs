# sources/test-tools/strace/tests/nfnetlink_acct.c

Purpose: tests nfnetlink accounting subsystem type decoding for `NFNL_SUBSYS_ACCT` messages.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_NETFILTER)`, `sendto`, `struct nlmsghdr`, `NFNL_SUBSYS_ACCT`, `NFNL_MSG_ACCT_*`, `NFNL_MSG_BATCH_BEGIN`, and `NLM_F_REQUEST`.

Control flow: the file sends header-only nfnetlink messages for accounting command names and selected flag combinations, including known and unknown command values, then prints expected symbolic names.

State and persistence: synthetic messages only; no accounting objects are created or deleted.

Dependencies and integration points: relies on `nfnetlink.h`, `nfnetlink_acct.h`, and strace’s nfnetlink message-type decoder.

Risks and edge cases: subsystem/command packing and command availability across kernel headers are the primary risks. Unknown command fallback must remain stable.

Test signals: expected output shows `NFNL_SUBSYS_ACCT<<8|...` style symbolic decoding and exits cleanly.
