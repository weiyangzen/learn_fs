<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp.c -->
# sources/test-tools/strace/tests/nlattr_ifla_xdp.c

Purpose: checks nested `IFLA_XDP` decoding for XDP program fd, attach state, flags, program IDs, and expected fd fields.

Important APIs/types/functions: includes `rtnl_ifla_xdp_attrs` xlat, `nlattr_ifla.h` with `IFLA_ATTR IFLA_XDP`, and uses `TEST_NESTED_NLATTR_OBJECT(_EX)` with int32/u32/u8 payloads. `FD9_PATH` is optionally appended by the `-y` wrapper.

Control flow: sends `IFLA_XDP_FD`, multiple `IFLA_XDP_ATTACHED` enum values including unknown fallbacks, `IFLA_XDP_FLAGS`, program ID attributes, and two `IFLA_XDP_EXPECTED_FD` cases including fd 9 path-aware output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on link/XDP UAPI, xlat mode, `/proc/self/fd` for fd path rendering, and strace's link XDP decoder. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; # include "xlat/rtnl_ifla_xdp_attrs.h"; ... (9 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_XDP; # define FD9_PATH "".

Risks: new XDP attach states or flags can alter expected symbolic names. The path-aware variant depends on `/dev/full` and proc fd availability.

Test signals: validates scalar, enum, bitmask, fd, and fd-path rendering for XDP attributes. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_xdp.c` has 98 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_xdp.c -->
