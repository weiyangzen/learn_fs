# sources/test-tools/ltp/testcases/kernel/syscalls/mlock/mlock03.c

Purpose: This case is a regression test on old RHEL5. Stack size mapping is decreased through mlock/munlock call. See the following url: https://bugzilla.redhat.com/show_bug.cgi?id=643426 This is to test kernel if it has a problem with shortening [stack] mapping through several loops of mlock/munlock of /proc/self/maps. From: munlock 76KiB bfef2000-bff05000 rw-p 00000000 00:00 0 [stack] To: munlock 44KiB bfefa000-bff05000 rw-p 00000000 00:00 0 [stack] with more iterations - could drop to 0KiB.

Important APIs/types/functions: mlock, munlock, tst_test, tst_safe_stdio, TST_KB, SAFE_FOPEN, tst_brk, tst_res, SAFE_FCLOSE; local functions detected: verify_mlock; key constants/macros: No prominent local constants beyond included headers.

Control flow: test_all runs one whole-file scenario. Local helper functions: verify_mlock.

State and persistence behavior: anonymous/file-backed memory mappings whose residency/locking/advice state is inspected; procfs files parsed for kernel-visible state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: page size, memory pressure, limits, and overcommit can affect observable residency/locking.

Test signals: explicit TPASS/TFAIL result messages; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: Record the initial stack size. Record the final stack size.
