<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c -->
# sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c

Purpose: stress-tests decoding of nested `IFLA_LINKINFO` attributes, including `IFLA_INFO_KIND`, `DATA`, `XSTATS`, `SLAVE_KIND`, and `SLAVE_DATA` for many link kinds and bridge/tun/can-specific payloads.

Important APIs/types/functions: defines macro helpers `TEST_UNKNOWN_TUNNELS`, `TEST_LINKINFO_`, `TEST_LINKINFO`, and `TEST_NESTED_LINKINFO` to synthesize kind strings and nested attributes. Uses route netlink helpers from `nlattr_ifla.h`, `xmalloc`, link xlat tables, `clock_t_str`, `ifindex_lo`, and Linux bridge/tun/can structs such as `br_boolopt_multi` and CAN stats.

Control flow: begins with unknown `IFLA_INFO_*` cases, iterates unsupported and supported tunnel kind strings, then performs deep bridge data checks for clock, scalar, ethernet protocol, bridge IDs, boolean options, multicast querier state, tun owner/group/type/queue fields, CAN xstats, and bridge slave-data/brport fields.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on `linux/if_bridge.h`, `linux/if_link.h`, rtnetlink xlat tables, and strace's linkinfo decoders selected by kind string. It integrates multiple nested attribute levels and validates fallback behavior for unsupported kinds. Source includes observed: #include "tests.h"; #include <inttypes.h>; #include <math.h>; #include <stdio.h>; #include <stddef.h>; #include <unistd.h>; #include <arpa/inet.h>; #include "test_nlattr.h"; ... (17 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_LINKINFO; #define COMMA ,; #define TEST_UNKNOWN_TUNNELS(fd_, nlh0_, kindtype_, objtype_, objtype_str_, \; #define TEST_LINKINFO_(fd_, nlh0_, kindtype_, nla_type_, nla_type_str_,	\; #define TEST_LINKINFO(fd_, nlh0_, kindtype_, nla_type_, tuntype_,	\; #define TEST_NESTED_LINKINFO(fd_, nlh0_, kindtype_,			\; #define QSTATE_NLA(type_, type_str_, field_, crop_str_, str_, ...)	\.

Risks: this fixture is sensitive to kind-string dispatch changes, nesting length/alignment, endian formatting, and UAPI additions. A new supported kind can intentionally break 'unknown tunnel' expectations, which is a useful but noisy signal.

Test signals: strong coverage of full, cropped, and overlong payloads; nested arrays; xlat known/unknown output; ifindex names; clock strings; and bridge/tun/can decoder paths. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c` has 1115 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_linkinfo.c -->
