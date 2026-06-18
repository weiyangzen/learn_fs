<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ifindex.c -->
# sources/test-tools/strace/tests/ifindex.c

## Purpose
Covers strace self-test coverage for `ifindex`. Source comments describe: Proxy wrappers for if_nametoindex. !HAVE_IF_INDEXTONAME Source read: 35 lines, 453 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", <net/if.h>; defines: none; C functions: ifindex_lo.

## Control Flow
Straight-line C test code built around helper macros and expected-output printing.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on `tests.h`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: main risk is drift between kernel behavior and the expected strace rendering. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ifindex.c -->
