# sources/test-tools/strace/tests/netlink_audit--pidns-translation.c

Purpose: compiles the audit netlink test with pid namespace translation enabled by defining `PIDNS_TRANSLATION` before including `netlink_audit.c`.

Important APIs, types, and helpers: inherits `sendto`, `struct nlmsghdr`, `AUDIT_GET`, `NETLINK_AUDIT`, `pidns_print_leader`, `pidns_pid2str`, and `create_nl_socket` from the included file.

Control flow: this wrapper has no independent runtime control flow. The included implementation initializes pid namespace testing, sends an audit netlink header whose `nlmsg_pid` is `getpid()`, and prints the translated pid suffix.

State and persistence: no persistent state beyond the temporary netlink socket. The compile-time define changes how pid namespace annotations are expected.

Dependencies and integration points: integrates with the pid namespace variant of strace tests. It depends on the base audit netlink decoder test and the harness support for running pid namespace translation checks.

Risks and edge cases: failures can arise from pid namespace support, base file changes, or mismatch between host and translated pid output.

Test signals: the output should match the base audit test with pid namespace translation details included for `nlmsg_pid`.
