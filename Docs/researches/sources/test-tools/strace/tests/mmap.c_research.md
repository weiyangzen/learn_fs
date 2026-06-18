# sources/test-tools/strace/tests/mmap.c

Purpose: `mmap.c` is a focused strace test/helper source in the `mmap decoder exercise` family. It builds a narrow scenario, invokes libc or raw syscall-facing APIs, and prints or enables expected-output checks for the surrounding testsuite.

Important APIs/types/functions: Complete-read metadata: 134 line(s), 3950 byte(s); classification `mmap decoder exercise`; functions `main`; syscall markers none visible in this file. Source-specific note: The mmap test intentionally prints different flag/protection/fd/offset combinations and is reused by `mmap64.c` and xlat wrappers to verify mmap argument rendering. Key includes are `tests.h`, `stdio.h`, `stdint.h`, `unistd.h`, `limits.h`, `sys/mman.h`. Key macros/compile switches are none visible in this file.

Control flow: Runtime starts in `main` when present, prepares tail-allocated buffers or kernel-visible structures, calls helper functions (`main`), invokes syscall targets (none visible in this file), records `sprintrc`/errno results where applicable, and prints expected strace lines. The file contains 0 explicit loop construct(s), usually to cover flag tables, pointer cases, sizes, or success/failure matrices.

State and persistence behavior: Persistent repository state is not changed by this source; runtime state is test-local. mapped memory is used as syscall input/output state. Cleanup is handled by test harness process exit or explicit close/unlink paths when the test creates named resources.

Dependencies and integration points: Dependencies are primarily `tests.h`, `stdio.h`, `stdint.h`, `unistd.h`, `limits.h`, `sys/mman.h`. Important compile-time knobs are none visible in this file. Integration is through the strace testsuite build system (`gen_tests.in`, per-test expected-output rules, xlat mode variants, and shell harnesses), which compiles this source or includes it from wrapper variants and compares stdout against strace output. Local integration signals: strace testsuite helpers.

Risks: raw/verbose/abbrev xlat formatting must stay aligned with decoder output.

Test signals: Test signals are generated stdout/stderr lines plus harness exit status. This source has 23 explicit print call(s). Strong signals: return-code string comparison via `sprintrc`, symbolic flag/xlat output comparison. A useful regression check is running the named strace test under all configured personalities and xlat modes that include this file.
