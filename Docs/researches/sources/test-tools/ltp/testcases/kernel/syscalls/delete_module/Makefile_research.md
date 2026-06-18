<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile -->
# sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile

Purpose: Build integration for the LTP delete_module syscall subdirectory. It selects local test binaries, filters unsupported builds, and hooks the directory into the shared LTP syscall make rules.

Important APIs/types/functions: This is make metadata rather than C code. Key integration variables are `obj-m := dummy_del_mod.o dummy_del_mod_dep.o`, `top_srcdir		?= ../../../..`, `REQ_VERSION_MAJOR	:= 2`, `REQ_VERSION_PATCH	:= 6`, `MAKE_TARGETS		:= delete_module01 delete_module02 delete_module03 \`. Include edges are `include $(top_srcdir)/include/mk/testcases.mk`, `include $(top_srcdir)/include/mk/module.mk`, `include $(top_srcdir)/include/mk/generic_leaf_target.mk`.

Control flow: GNU make evaluates the local variables, applies any architecture or libc filters, then includes the common LTP rules that compile and install the named test programs.

State and persistence behavior: The file does not create runtime state itself. Its persistent effect is the set of binaries and module objects produced under the LTP build tree.

Dependencies and integration points: It depends on the parent LTP build system, common syscall-test rules, and the source files in `sources/test-tools/ltp/testcases/kernel/syscalls/delete_module`. Target signals: MAKE_TARGETS		:= delete_module01 delete_module02 delete_module03 \.

Risks: Build filters can silently omit coverage on some architectures or libc combinations. Missing library variables or module-build hooks would surface as compile or link failures before runtime.

Test signals: Successful make evaluation should produce the selected LTP test binaries without changing runtime kernel state; failures are compile, link, missing-header, or filtered-target signals.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/delete_module/Makefile -->
