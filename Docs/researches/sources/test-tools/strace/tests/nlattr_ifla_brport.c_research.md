<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport.c -->
# sources/test-tools/strace/tests/nlattr_ifla_brport.c

Purpose: validates `IFLA_PROTINFO` decoding when `ifi_family` is `AF_BRIDGE`, specifically bridge-port attributes under the `IFLA_BRPORT_*` namespace.

Important APIs/types/functions: includes `nlattr_ifla.h` with `IFLA_ATTR IFLA_PROTINFO`, `IFLA_AF AF_BRIDGE`, and uses `check_u8_nlattr`, `check_u16_nlattr`, `check_x16_nlattr`, `check_u32_nlattr`, `check_clock_t_nlattr`, plus `TEST_NESTED_NLATTR_OBJECT_EX_`. It exercises `struct ifla_bridge_id` and ifindex formatting via `ifindex_lo()`.

Control flow: builds one synthetic RTM_GETLINK message, first checks undecoded/unknown bridge-port attributes, then loops over grouped u8, u16, x16, u32, clock_t, bridge-id, and ifindex attributes. It tests both raw numeric ifindex and loopback-name-aware output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on bridge rtnetlink UAPI in `linux/if_link.h`, proc fd availability, and strace's `decode_ifla_protinfo` bridge branch. The `-X*` wrappers compile this same body under alternate xlat modes. Source includes observed: #include "tests.h"; #include <stdio.h>; #include <inttypes.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; ... (9 total). Key defines/macros observed: #define IFLA_ATTR IFLA_PROTINFO; #define IFLA_AF AF_BRIDGE; #define IFLA_AF_STR "AF_BRIDGE".

Risks: bridge-port attribute churn can make known/unknown lists stale. Timer formatting depends on strace's clock_t decoder, and ifindex output depends on loopback discovery and `-y`/xlat mode expectations.

Test signals: broad coverage across scalar widths, bridge IDs, timers, and loopback ifindex output gives good regression signals for bridge-port nlattr decoding. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_brport.c` has 214 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_brport.c -->
