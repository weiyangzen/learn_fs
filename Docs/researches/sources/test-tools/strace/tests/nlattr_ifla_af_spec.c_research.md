<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_spec.c -->
# sources/test-tools/strace/tests/nlattr_ifla_af_spec.c

Purpose: verifies strace decoding of `IFLA_AF_SPEC` nested rtnetlink attributes for link messages across unknown address families and implemented AF_INET, AF_BRIDGE, AF_INET6, and AF_MCTP subtrees.

Important APIs/types/functions: uses `test_nlattr.h` macros, `create_nl_socket(NETLINK_ROUTE)`, `midtail_alloc`, `init_ifinfomsg`/`print_ifinfomsg` from `nlattr_ifla.h`, generated xlat tables for `rtnl_ifla_af_spec_inet_attrs` and `rtnl_ifla_af_spec_inet6_attrs`, and `check_ifla_af_inet6` from `nlattr_ifla_af_inet6.h`. Local `AF_SPEC_FUNCS` builds nested initializers/printers for AF_INET, AF_INET6, AF_MCTP, and bridge tunnel info.

Control flow: opens a route netlink socket, fills reusable pattern buffers, exhaustively probes unknown outer and inner AF attributes, then executes targeted nested checks for AF_INET config arrays, bridge flags/modes/VLAN/tunnel attributes, the shared IPv6 AF helper, and MCTP `IFLA_MCTP_NET`/`PHYS_BINDING` fields.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on Linux `if_link`, bridge, rtnetlink headers, xlat tables, loopback ifindex/proc fd availability, and the strace rtnl link decoder. It integrates with the netlink attribute test macro layer that synthesizes netlink messages and compares decoder output. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <stdio.h>; #include <stddef.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_bridge.h>; ... (16 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_AF msg_af; #define IFLA_AF_STR msg_af_str; #define IFLA_ATTR IFLA_AF_SPEC; #define AF_SPEC_FUNCS(family_)						\.

Risks: high risk of kernel UAPI drift because bridge, IPv6, and MCTP attribute tables evolve. Nested offset calculations (`nla += 1`, adjusted `NLA_HDRLEN` depths) are fragile, and endian-sensitive bridge/VLAN expectations must stay aligned with decoder behavior.

Test signals: successful execution prints decoded AF names, known/unknown xlat fallbacks, cropped hex payloads, clock/value forms, and the final exit marker; failures point to changed AF-specific decoder coverage or stale xlat constants. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_af_spec.c` has 360 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_af_spec.c -->
