<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp--pidns-translation.c -->
# sources/test-tools/strace/tests/getpgrp--pidns-translation.c

## Purpose
Variant wrapper that includes `getpgrp.c` after defining `PIDNS_TRANSLATION`. It lets the same compiled test exercise a different strace output mode without duplicating the base implementation. Source read: 2 lines, 47 bytes.

## Important APIs, Types, And Functions
includes/imports: "getpgrp.c"; defines: PIDNS_TRANSLATION.

## Control Flow
Preprocessor control flow only: define `PIDNS_TRANSLATION`, include `getpgrp.c`, and inherit that file's `main` and helper functions.

## State And Persistence Behavior
no persistent repository state; runtime state is process-local variables plus transient kernel return values.

## Dependencies And Integration Points
Depends on shared implementation `getpgrp.c`. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: pid namespace translation is sensitive to namespace support and parent/child synchronization. Test signals: successful compilation and harness comparison are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/getpgrp--pidns-translation.c -->
