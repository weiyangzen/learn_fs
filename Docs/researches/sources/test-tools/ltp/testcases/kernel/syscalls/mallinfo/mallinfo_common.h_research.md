# sources/test-tools/ltp/testcases/kernel/syscalls/mallinfo/mallinfo_common.h

Purpose: Shared header/support code for the `mallinfo` LTP syscall tests. It centralizes declarations, constants, or helper routines used by sibling test programs.

Important APIs/types/functions: tst_test, tst_res; local functions detected: print_mallinfo, print_mallinfo2; key constants/macros: MALLINFO_COMMON_H, P, P2

Control flow: Included by sibling tests; exposes inline/static helpers and shared constants/types. Visible helpers: print_mallinfo, print_mallinfo2.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: main risk is environmental mismatch between the test host and the kernel feature being asserted.

Test signals: successful compilation and LTP harness execution. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
