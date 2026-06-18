<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile

Purpose: build metadata for the LTP syscall tests in this directory; it tells the shared LTP make system how to compile local test executables and any helper variants.

Important APIs/types/functions: key make directives are `top_srcdir		?= ../../../..; include $(top_srcdir)/include/mk/testcases.mk; include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: make loads the top-level testcase rules, applies directory-local flags or target filters, then delegates binary creation to the generic leaf target include.

State and persistence behavior: this file has no runtime state. Its persistent effect is the set of binaries and compile flags produced for the syscall tests.

Dependencies and integration points: integrates with shared LTP make fragments under `include/mk/testcases.mk` and `generic_leaf_target.mk`. It is the build entry point for the `pidfd_open` test folder.

Risks and test signals: incorrect flags, missing helper libraries, or omitted 64-bit variants reduce runtime coverage before any test executes. Successful compilation and expected executable/helper presence are the primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/pidfd_open/Makefile -->
