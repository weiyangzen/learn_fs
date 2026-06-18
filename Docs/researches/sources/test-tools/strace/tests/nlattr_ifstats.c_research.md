<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats.c -->
# sources/test-tools/strace/tests/nlattr_ifstats.c

Purpose: exercises RTM_GETSTATS `struct if_stats_msg` attribute decoding, including link stats64, bridge/bond extended stats, offload stats, and AF_MPLS stats under `IFLA_STATS_AF_SPEC`.

Important APIs/types/functions: local `init_ifstats`, nested-function macro `DEF_NLATTR_FUNCS_NESTED`, helpers `print_stats_64`, `check_stats_64`, `fmt_str`, `print_mcast_stats`, `check_xstats`, `check_stats_offload`, `check_stats_af_generic`, and `check_stats_af_mpls`. Uses `rtnl_link_stats64`, bridge VLAN/mcast/STP xstats, bond 802.3ad counters, `mpls_link_stats`, and multiple xlat tables.

Control flow: checks unknown top-level stats attrs, decodes `IFLA_STATS_LINK_64`, runs bridge and bond xstats for both normal and slave top-level attrs, checks offload CPU-hit stats, generically probes AF-specific unknown families, then decodes MPLS link stats.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_link.h`, bonding, bridge, MPLS headers, address-family/xstats xlat tables, and strace's RTM_GETSTATS decoder. Source includes observed: #include "tests.h"; #include <arpa/inet.h>; #include <inttypes.h>; #include <linux/ip.h>; #include <netinet/in.h>; #include <stdbool.h>; #include <stdint.h>; #include <stdio.h>; ... (26 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define DEF_NLATTR_FUNCS_NESTED(sfx_, attr_var_, attr_str_var_,		\; #define PR_FIELD_(pfx_, field_) \; #define FIELD_STR_(field_) \.

Risks: this is broad and sensitive to struct growth (`rx_nohandler`, `rx_otherhost_dropped`), nested xlat additions, and UAPI additions to stats families. Global l1/l2/l3 attr variables make ordering and nested printer setup important.

Test signals: very high-value regression coverage for nested stats decoders, cropped-vs-full struct lengths, unknown fallback, and xlat/raw/verbose mode differences. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifstats.c` has 789 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifstats.c -->
