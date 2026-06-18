# sources/test-tools/strace/tests/nlattr_cachereport.c

Purpose: tests route-netlink cache report (`RTM_NEWCACHEREPORT`) attribute decoding, including address-family dependent multicast route cache payloads and xlat rendering modes.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct rtgenmsg`, `RTM_NEWCACHEREPORT`, `CACHE_REPORT_*`, `struct mfcctl`, `struct mf6cctl`, `TEST_NETLINK_`, `TEST_NLATTR_`, `TEST_NLATTR_OBJECT_EX_`, `xlat/addrfams.h`, and global `af`/`af_str` formatting state.

Control flow: initializes route-generator messages, sends bare cache report messages, then tests attributes for IPv4 and IPv6 multicast cache reports with normal, short, and object-specific payloads. It adapts expected output according to xlat mode macros.

State and persistence: uses global variables to track the current address family string for expected output. No kernel route cache state is changed.

Dependencies and integration points: relies on route, IPv4 multicast, IPv6 multicast, and xlat headers plus strace nlattr helper macros. Included by three wrapper files for xlat output variants.

Risks and edge cases: address-family-specific object size differences, xlat mode conditionals, and short object reads are the major risks.

Test signals: expected output decodes `RTM_NEWCACHEREPORT`, `rtgen_family`, cache report attributes, IPv4/IPv6 multicast fields, and xlat-mode-specific values.
