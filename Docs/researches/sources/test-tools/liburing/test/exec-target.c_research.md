<!-- BEGIN_FILE_RESEARCH: sources/test-tools/liburing/test/exec-target.c -->
## sources/test-tools/liburing/test/exec-target.c

Purpose: minimal executable target used by other tests that need a known successful `exec` destination.

Important APIs/types/functions: only `main`.

Control flow: `main` returns zero unconditionally.

State and persistence behavior: no state is created, read, or persisted.

Dependencies and integration points: integrates with tests that fork/exec another binary and need a stable target whose success is independent of io_uring behavior.

Risks: this file provides no direct io_uring signal. Its usefulness depends on external tests invoking it correctly.

Test signals: process exit status zero indicates the exec target ran.
<!-- END_FILE_RESEARCH: sources/test-tools/liburing/test/exec-target.c -->
