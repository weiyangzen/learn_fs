<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile

Purpose: LTP leaf build file for the `writev` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.

Directory-specific integration: `writev03` adds `-pthread` and `-lrt` because that regression test uses LTP fuzzy synchronization, atomics, and threaded racing around page-faulted iovecs. Other `writev` tests use the generic leaf rules.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/writev/Makefile -->
