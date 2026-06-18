<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ioperm.c -->
# sources/test-tools/strace/tests/ioperm.c

Purpose: Tests strace decoding of the `ioperm` syscall on architectures where `__NR_ioperm` exists.

Important APIs/types/functions: Uses direct `syscall(__NR_ioperm, ...)`, `kernel_ulong_t` fixture values, `sprintrc`, and `SKIP_MAIN_UNDEFINED`.

Control flow: Calls `ioperm` once with deliberately oversized/bogus `from`, `num`, and `turn_on` values, prints low-width argument formatting and the syscall result, then exits.

State/persistence behavior: The bogus request is expected to fail, so no I/O permission bitmap state is granted. There is no persistent state.

Dependencies: Architecture syscall availability through `scno.h` and Linux permission checks.

Integration points: Verifies scalar syscall argument decoding and skip behavior on unsupported architectures.

Risks: On unusual kernels the failure errno may vary, but formatting should remain stable. Running as privileged code still uses nonsensical ranges.

Test signals: One `ioperm(...) = ...` line or a skip build when the syscall number is unavailable.

Source read signal: complete file read for this research pass; file size 32 line(s), 527 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ioperm.c -->
