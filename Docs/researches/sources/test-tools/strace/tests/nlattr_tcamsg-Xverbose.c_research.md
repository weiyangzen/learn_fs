<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c -->
# sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c

Purpose: compile-time variant wrapper for `nlattr_tcamsg.c`. It exists so the same base fixture is built under a different strace output mode or path/fd printing mode without duplicating the test body.

Important APIs/types/functions: the file contains only preprocessor configuration (`XLAT_VERBOSE=1`) followed by `#include "nlattr_tcamsg.c"`. The effective APIs, syscall calls, helper functions, and structs are inherited from the included base source.

Control flow: preprocessing defines the variant macros first, includes `nlattr_tcamsg.c`, and therefore compiles the base `main` with alternate xlat/path/verbose behavior. Runtime control flow is exactly the base fixture's flow, but expected printf text changes according to the macros.

State/persistence behavior: these tests do not persist application state beyond temporary trace fixtures. They allocate synthetic netlink/syscall argument buffers with test helpers, may create or remove short-lived files or sockets, print the expected strace line to stdout, and terminate with `+++ exited with 0 +++` when the decoder behavior matches the fixture contract.

Dependencies/integration points: depends directly on `nlattr_tcamsg.c` and indirectly on the same strace test harness headers, kernel UAPI headers, and decoder under test as the base. Integration is through the test-suite target that runs this wrapper under the corresponding `-X`, `-y`, `-P`, or verbosity mode. Source includes observed: #include "nlattr_tcamsg.c". Key defines/macros observed: #define XLAT_VERBOSE 1.

Risks: the file is intentionally tiny, so the main risk is macro drift: changing the base fixture without considering these variants can make raw/verbose/abbrev/path expectations stale. Another risk is assuming the wrapper adds behavior; it only changes compile-time formatting mode.

Test signals: a healthy run compiles the wrapper, exercises the included base test body, and emits base syscall/netlink traces with the variant's expected symbolic/raw/verbose/path formatting. Non-empty generated research confirms the wrapper-to-base mapping is preserved. Source-read signal: `sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c` has 2 source lines in this checkout, and this report preserves the source-tree-aligned path for reconciliation.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/nlattr_tcamsg-Xverbose.c -->
