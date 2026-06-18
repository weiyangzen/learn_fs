# sources/test-tools/strace/tests/nlattr_ifaddrmsg.c

Purpose: validates nlattr decoding for interface address messages across IPv4, IPv6, and non-IP family contexts.

Important APIs, types, and helpers: `create_nl_socket(NETLINK_ROUTE)`, `struct ifaddrmsg`, `IFA_*`, `IFA_F_*`, `RTM_NEWADDR`, `TEST_NLATTR_`, `TEST_NLATTR`, `TEST_NLATTR_OBJECT`, `inet_pton`, and the `SET_IFA_FAMILY` helper macro.

Control flow: initializes an ifaddr header, switches address families, then tests local/address/broadcast/anycast/cacheinfo/flags attributes with family-appropriate formatting.

State and persistence: no interface addresses are created or modified. Family selection is in local message buffers only.

Dependencies and integration points: depends on `linux/if_addr.h`, route netlink decoder tables, and nlattr helpers.

Risks and edge cases: IPv4 versus IPv6 address length interpretation, flag bitmask rendering, and raw fallback for unexpected families are the main risks.

Test signals: expected output decodes `IFA_*` attributes with correct address and cacheinfo formatting.
