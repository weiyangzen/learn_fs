# sources/test-tools/ltp/testcases/kernel/syscalls/fchdir/Makefile

Purpose: builds the `fchdir` syscall tests as a standard LTP leaf testcase directory.

Important APIs/types/functions: GNU make variables `top_srcdir`, `include $(top_srcdir)/include/mk/testcases.mk`, and `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: the file sets a default relative top source directory, imports common testcase build rules, then imports generic leaf targets that compile the C files in the directory.

State/persistence behavior: no runtime state. Build state is delegated to the LTP make infrastructure and generated object/binary outputs.

Dependencies/integration: depends on LTP's common make fragments for compiler flags, testcase discovery, install rules, and cleanup.

Risks/test signals: risk is low; build failure would indicate missing make infrastructure or incompatible directory layout rather than syscall test behavior.
