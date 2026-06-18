<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am -->
# sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am

**Purpose**
This Automake file builds and runs the `aulast` linked-list unit test.

**Important APIs, Types, And Functions**
It declares `noinst_PROGRAMS = aulast_llist_test` and `TESTS = aulast_llist_test`. The test sources are the test file plus `${top_srcdir}/tools/aulast/aulast-llist.c`, and include paths point at the `aulast` source directory. If ASAN is enabled, it applies sanitizer flags; otherwise it links statically.

**Control Flow**
During `make check` in the `aulast/test` directory, Automake compiles the list implementation into the test binary and executes it.

**State And Persistence**
No runtime state is defined by the makefile. Build outputs are non-installed.

**Dependencies And Integration Points**
The test intentionally links the production list implementation directly, giving focused coverage without building the entire `aulast` binary.

**Risks**
Static linking in the non-ASAN path can expose platform/toolchain differences. The test only covers the linked-list layer and not auparse-driven session parsing.

**Test Signals**
Successful execution of `aulast_llist_test` indicates key session-list operations remain stable.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/tools/aulast/test/Makefile.am -->
