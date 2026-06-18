<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_protinfo.c

Purpose: validates generic `IFLA_PROTINFO` behavior across address families: unknown families should remain hex payloads, AF_BRIDGE is delegated to `nlattr_ifla_brport`, and AF_INET6 is decoded through the shared IPv6 helper.

Important APIs/types/functions: local `init_ifinfomsg`, `init_ifinfomsg_protinfo`, `print_ifinfomsg`, and `print_ifinfomsg_protinfo`; uses `addrfams` xlat, `check_ifla_af_inet6`, and route netlink helpers.

Control flow: iterates all 256 possible `ifi_family` values except AF_BRIDGE and AF_INET6, expecting undecoded hex payloads for `IFLA_PROTINFO`; then sets AF_INET6 and runs `check_ifla_af_inet6` inside one nested `IFLA_PROTINFO` level.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on rtnetlink, ARP/link headers, xlat address families, loopback ifindex, and the strace link decoder's family-specific protinfo dispatch. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <netinet/in.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; #include <stdio.h>; #include "test_nlattr.h"; ... (11 total).

Risks: newly supported address-family protinfo decoders can change the expected unknown fallback. The skip list must remain sorted/accurate so bridge and IPv6 coverage stays in their specialized fixtures.

Test signals: exhaustive family iteration is a strong negative-coverage signal; IPv6 positive coverage verifies nested AF-specific decoding through a shared helper. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_protinfo.c` has 127 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_protinfo.c -->
