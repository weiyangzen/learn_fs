<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/hexdump_strdup.c -->
# sources/test-tools/strace/tests/hexdump_strdup.c

## Purpose
Covers strace self-test coverage for `hexdump_strdup`. Source comments describe: Make a hexdump copy of C string Source read: 45 lines, 853 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <assert.h>, <stdlib.h>, <string.h>; defines: none; C functions: hexdump_memdup, hexdump_strdup.

## Control Flow
nested loops cover flag, pointer, size, fd, and translation-mode combinations.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/hexdump_strdup.c -->
