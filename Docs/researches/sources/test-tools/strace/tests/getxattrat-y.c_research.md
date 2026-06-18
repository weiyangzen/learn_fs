<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-y.c -->
# sources/test-tools/strace/tests/getxattrat-y.c

## Purpose
Variant wrapper that includes `getxattrat.c` after defining `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 4 lines, 129 bytes.

## Important APIs, Types, And Functions
includes/imports: "getxattrat.c"; defines: FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE.

## Control Flow
Preprocessor control flow only: define `FD_PATH, SKIP_IF_PROC_IS_UNAVAILABLE`, include `getxattrat.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `/proc/self/fd`, shared implementation `getxattrat.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: path-decoding variants require procfs fd links. Test signals: skip paths report exit 77 rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getxattrat-y.c -->
