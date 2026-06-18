<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fill_memory.c -->
# sources/test-tools/strace/tests/fill_memory.c

## Purpose
Covers strace self-test coverage for `fill_memory`. Source read: 76 lines, 1384 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h"; defines: none; C functions: fill_memory_ex, fill_memory, fill_memory16_ex, fill_memory16, fill_memory32_ex, fill_memory32, fill_memory64_ex, fill_memory64.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fill_memory.c -->
