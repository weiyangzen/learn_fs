# sources/test-tools/ltp/testcases/kernel/syscalls/llistxattr/Makefile

Purpose: Build recipe for the LTP `llistxattr` syscall testcase directory. It pulls in the common LTP testcase make rules and generic leaf target; local build knobs include top_srcdir		?= ../../../...

Important APIs/types/functions: Make variables or local declarations only; local functions detected: none; key constants/macros: No prominent local constants beyond included headers.

Control flow: Make evaluates `top_srcdir`, includes the shared testcase rules, applies any local CFLAGS/LDLIBS, and lets `generic_leaf_target.mk` discover/build the leaf tests in this directory.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP build system include/mk/testcases.mk and generic_leaf_target.mk. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: build correctness depends on inherited LTP make variables and any local flags staying in sync with source assumptions.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
