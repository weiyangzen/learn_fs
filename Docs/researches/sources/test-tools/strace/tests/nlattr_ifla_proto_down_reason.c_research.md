<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c -->
# sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c

Purpose: tests `IFLA_PROTO_DOWN_REASON` nested attributes, distinguishing undecoded reason attributes from known mask/value u32 attributes.

Important APIs/types/functions: includes `rtnl_ifla_proto_down_reason_attrs` xlat in macro-only mode, `nlattr_ifla.h` with `IFLA_ATTR IFLA_PROTO_DOWN_REASON`, and `TEST_NESTED_NLATTR_OBJECT_EX_`.

Control flow: sends invalid or unspecified reason attributes and expects quoted bytes, then sends `IFLA_PROTO_DOWN_REASON_MASK` and `VALUE` and expects hexadecimal u32 output.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends on route link decoder support for protocol-down reason subattributes and Linux if_link definitions. Source includes observed: #include "tests.h"; #include <stdio.h>; #include "test_nlattr.h"; #include <linux/if.h>; #include <linux/if_arp.h>; #include <linux/if_link.h>; #include <linux/rtnetlink.h>; # include "xlat/rtnl_ifla_proto_down_reason_attrs.h"; ... (9 total). Key defines/macros observed: #define XLAT_MACROS_ONLY; #define IFLA_ATTR IFLA_PROTO_DOWN_REASON.

Risks: UAPI additions can reclassify unknown attributes; byte-order of the test union must remain compatible with expected escaped bytes.

Test signals: checks both fallback and semantic u32 paths for proto-down reason decoding. Source-read signal: `sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c` has 76 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_ifla_proto_down_reason.c -->
