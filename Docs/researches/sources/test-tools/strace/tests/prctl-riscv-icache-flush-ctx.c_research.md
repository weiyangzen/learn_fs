<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c -->
# sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c

## Purpose

`sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c` is a C test program in the strace tests tree. It provides prctl decoder coverage for one PR_* operation family or xlat rendering mode, including raw, abbreviated, verbose, success-injection, and pid namespace translation variants where applicable. The source was read as a complete 65-line file for this report.

## Important APIs, Types, and Functions

includes: `tests.h`, `scno.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `linux/prctl.h`. functions: `main`. types: `strval_klong`. macros: none found in this file. direct syscall numbers: `__NR_prctl`. notable constants/xlats: `PR_RISCV_V_SET_CONTROL`, `PR_RISCV_V_GET_CONTROL`, `PR_RISCV_CTX_SW_FENCEI_ON`, `PR_RISCV_CTX_SW_FENCEI_OFF`, `PR_RISCV_SCOPE_PER_PROCESS`, `PR_RISCV_SCOPE_PER_THREAD`, `PR_RISCV_SET_ICACHE_FLUSH_CTX`, `PR_RISCV_CTX_`, `PR_RISCV_SCOPE_`. Source size: 65 lines, 1526 bytes.

## Control Flow

`main` initializes the local strace test harness, prepares syscall arguments, invokes the target syscall or helper, prints the expected trace line, and finishes with the canonical `+++ exited with 0 +++` marker. It directly exercises `__NR_prctl`. Loops over tables of options, flags, pointers, or malformed arguments to compare strace output against printf-generated expectations.

## State and Persistence Behavior

No durable repository or file-backed state is owned by the test itself; persistent output is the strace transcript consumed by the test harness.

## Dependencies and Integration Points

strace `tests.h` helpers for skips, error reporting, tail allocation, and result formatting; `scno.h` syscall-number indirection for portable direct `syscall` invocations; `xlat` tables and XLAT mode macros for symbolic, raw, abbreviated, and verbose rendering; Linux UAPI headers for syscall-specific constants and structs; POSIX libc/syscall APIs such as `syscall`, `fork`, `wait`, `open`, `poll`, `prctl`, or `ptrace`.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; pointer-boundary tests intentionally pass invalid addresses, so expected output must distinguish address printing from dereferenced structures; injection/success tests can mask real kernel return values and must keep skip counts synchronized with generated expected output.

## Test Signals

successful build of this file in the strace tests matrix; golden stdout/stderr comparison ending in `+++ exited with 0 +++`; expected xlat rendering for known constants plus unknown numeric fallback cases.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/prctl-riscv-icache-flush-ctx.c -->
