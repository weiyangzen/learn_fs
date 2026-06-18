# sources/test-tools/ltp/testcases/kernel/syscalls/migrate_pages/migrate_pages_common.c

Purpose: LTP testcase for `migrate_pages` behavior in `migrate_pages_common.c`. The file uses table-driven or harness-driven checks around the relevant syscall/library API.

Important APIs/types/functions: tst_resm; local functions detected: set_bit, check_ret, check_errno; key constants/macros: No prominent local constants beyond included headers.

Control flow: Control is centered on local helpers set_bit, check_ret, check_errno and the surrounding LTP harness.

State and persistence behavior: mostly local process state plus LTP harness result counters. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; NUMA-capable kernel/libnuma-style node topology. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
