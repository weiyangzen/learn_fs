<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile

Purpose: LTP leaf build file for the `wait` syscall test directory. It anchors this directory under the LTP kernel syscall test hierarchy and delegates target discovery, compilation rules, install layout, and harness metadata to the shared make infrastructure.

Important APIs/types/functions: defines `top_srcdir ?= ../../../..`, includes `include/mk/testcases.mk`, and includes `include/mk/generic_leaf_target.mk`. There are no local targets except where noted by the directory-specific report.

Control flow: GNU make resolves `top_srcdir`, loads the common testcase rules, then the generic leaf target builds the C test programs in this directory. State is build-time only: object files, binaries, and dependency tracking are handled by the common LTP rules rather than by this file.

Dependencies/integration: integrates the directory with the LTP build system and assumes the surrounding source tree provides the common mk fragments, compiler settings, and install/test metadata. Risks are mostly build-integration risks: changing includes or `top_srcdir` would orphan the tests from standard LTP discovery.

Test signals: successful make traversal should produce the directory's syscall test binaries; failures here indicate harness/build plumbing issues rather than runtime syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/wait/Makefile -->
