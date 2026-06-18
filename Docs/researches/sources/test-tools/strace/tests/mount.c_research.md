# sources/test-tools/strace/tests/mount.c

Purpose: `mount.c` is a focused strace test/helper source in the `mount decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 116 line(s), 3894 byte(s); classification `mount decoder exercise`; functions `main`; syscall markers none visible in this file. Key includes are `tests.h`, `stdio.h`, `unistd.h`, `sys/mount.h`. Key macros/compile switches are `MS_MGC_VAL`, `MS_RELATIME`, `str_unknown`, `str_submount_200`, `str_mgc_val`, `str_remount`, `str_bind`, `str_ro_nosuid_nodev_noexec`, `str_ro_nosuid_nodev_noexec_relatime`, `str_unknown`, ... (23 total).

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. tail-allocated memory is used to create valid, unterminated, and faulting user pointers at page boundaries. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `unistd.h`, `sys/mount.h`. Important compile-time knobs are `MS_MGC_VAL`, `MS_RELATIME`, `str_unknown`, `str_submount_200`, `str_mgc_val`, `str_remount`, `str_bind`, `str_ro_nosuid_nodev_noexec`, ... (23 total). Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output; faulting-pointer tests rely on precise page-boundary helper behavior.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 12 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
