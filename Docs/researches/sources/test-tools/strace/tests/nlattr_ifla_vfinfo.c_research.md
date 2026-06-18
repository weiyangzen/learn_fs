<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c

Purpose: validates nested `IFLA_VFINFO_LIST` decoding for virtual-function info, stats, VLAN lists, MAC/broadcast addresses, link states, trust/guid/rate fields, and ethernet protocol names.

Important APIs/types/functions: defines nested initializers/printers for `IFLA_VF_INFO`, `IFLA_VF_STATS`, and `IFLA_VF_VLAN_LIST`; uses many `struct ifla_vf_*` payloads, `check_u64_nlattr`, `TEST_NESTED_NLATTR_OBJECT_EX_`, `htons`, and xlat-aware MAC printing.

Control flow: probes unknown list and VF attributes, then exercises each structured VF payload (`MAC`, `VLAN`, `TX_RATE`, `SPOOFCHK`, `LINK_STATE`, `RATE`, `RSS_QUERY_EN`, stats, `TRUST`, GUIDs, VLAN info list, broadcast). Nested depth increases from top-level VF list to VF info to stats/VLAN subtrees.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h`, route netlink helpers, ethernet protocol xlat tables, and strace's `IFLA_VFINFO_LIST` decoder. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <stddef.h>; #include <stdio.h>; #include <arpa/inet.h>; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; ... (12 total). Key defines/macros observed: #define IFLA_ATTR IFLA_VFINFO_LIST.

Risks: VF UAPI evolves frequently; known/unknown attribute lists and struct field coverage can become stale. MAC string formatting changes under xlat mode are covered by wrappers but remain a maintenance point.

Test signals: strong positive coverage for every major VF payload family and negative coverage for unknown attrs at each nesting level. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c` has 403 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_vfinfo.c -->
