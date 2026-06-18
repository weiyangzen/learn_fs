<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_port.c -->
# sources/test-tools/strace/tests/nlattr_ifla_port.c

Purpose: checks `IFLA_PORT_SELF` nested port attributes in RTM_GETLINK messages, especially VF and VSI payload printing.

Important APIs/types/functions: uses `nlattr_ifla.h` with `IFLA_ATTR IFLA_PORT_SELF`, `TEST_NESTED_NLATTR_OBJECT`, and `struct ifla_port_vsi`. Fields are printed with `PRINT_FIELD_U` and quoted byte strings.

Control flow: creates a route netlink socket, allocates a message buffer, tests numeric `IFLA_PORT_VF`, then tests two `IFLA_PORT_VSI_TYPE` structures: one printable ASCII VSI type ID and one binary ID/pad case.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h` port attribute definitions and the strace rtnl link port decoder. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; #include "nlattr_ifla.h". Key defines/macros observed: #define IFLA_ATTR IFLA_PORT_SELF.

Risks: struct layout or padding changes can affect expected byte output. Binary string escaping must match strace's current quoting policy.

Test signals: validates both scalar VF output and structured VSI field decoding, including optional pad bytes. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_port.c` has 72 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_port.c -->
