# sources/test-tools/strace/tests/nlattr_fib_rule_hdr.c

Purpose: validates nlattr decoding for FIB rule messages, including address attributes, interface names, priorities, marks, uid ranges, and l3mdev/table fields.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct fib_rule_hdr`, `FRA_*`, `FR_ACT_*`, `TEST_NLATTR_`, `TEST_NLATTR_OBJECT`, `inet_pton`, `linux/fib_rules.h`, and IPv4/IPv6 address helpers.

Control flow: builds a FIB rule header, sends primitive attributes and object attributes for IPv4/IPv6 addresses and rule metadata, and loops through selected family-specific cases.

State and persistence: no real routing rules are added or removed; all messages are synthetic.

Dependencies and integration points: route nlattr decoder, fib rules UAPI, xlat tables for actions, flags, and attribute names.

Risks and edge cases: address-family-dependent payload interpretation, uid range object size, and unknown/raw attribute fallbacks are key boundaries.

Test signals: expected output shows decoded FIB rule header fields and structured `FRA_*` attribute payloads.
