<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/futex2_flags.h -->
# sources/test-tools/strace/tests/futex2_flags.h

## Purpose
Covers strace decoder coverage for `FUTEX2_`. Source comments describe: Check decoding of FUTEX2_* flags. FUTEX2_SIZE_U8 FUTEX2_SIZE_U16 FUTEX2_SIZE_U32 FUTEX2_SIZE_U64 FUTEX2_SIZE_U8|FUTEX2_NUMA FUTEX2_SIZE_U16|FUTEX2_MPOL FUTEX2_SIZE_U32|FUTEX2_PRIVATE FUTEX2_SIZE_U64|FUTEX2_NUMA|FUTEX2_PRIVATE FUTEX2_SIZE_U8|0xffffff70 FUTEX2_SIZE_U64|FUTEX2_NUMA|FUTEX2_MPOL" "|FUTEX2_PRIVATE|0xffffff70 Source read: 65 lines, 1427 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h"; defines: STRACE_TESTS_FUTEX2_FLAGS_H.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
No runtime state is owned here. The header contributes compile-time constants, declarations, or helper macros to including tests.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/futex2_flags.h -->
