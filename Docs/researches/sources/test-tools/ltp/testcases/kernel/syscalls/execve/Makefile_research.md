# sources/test-tools/ltp/testcases/kernel/syscalls/execve/Makefile

Purpose: Build leaf for the LTP syscall tests in this directory. It adds `CPPFLAGS += -I$(abs_srcdir)/../lib` so execve tests can include shared syscall-test helper headers.

Important APIs/types/functions: `top_srcdir`, `include/mk/testcases.mk`, optional per-target `CFLAGS`/`CPPFLAGS`, and `include/mk/generic_leaf_target.mk`.

Control flow: The makefile only sets local variables, includes the shared LTP testcase rules, and delegates target discovery/build/install behavior to the generic leaf target.

State and persistence behavior: It has no runtime state. Its persistent effect is build-system metadata that determines how the adjacent C test binaries are compiled.

Dependencies and integration points: Integrated with the LTP recursive make framework and inherits compiler, install, cleanup, and generated-target handling from the shared mk files.

Risks and test signals: Risk is mainly build integration drift: a missing include path, feature macro, or target-specific flag can make otherwise valid tests fail to build. Test signal is successful compilation of all sibling test programs.
