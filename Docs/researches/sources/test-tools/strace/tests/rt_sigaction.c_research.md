<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.c -->
# sources/test-tools/strace/tests/rt_sigaction.c

## Purpose

`sources/test-tools/strace/tests/rt_sigaction.c` sets signal handlers and raises signals to exercise rt_sigaction-related trace normalization in the strace tests tree. Source read: complete file, 48 lines, 983 bytes, sha256 `1f9e3647c201aec3`.

## Important APIs, Types, and Functions

Includes: `<assert.h>`, `<stdlib.h>`, `<unistd.h>`, `<signal.h>`. Compile-time macros: none found. Functions/helpers: `handle_signal`, `main`. Direct syscall numbers: none found. Notable constants/xlats: `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGTERM`, `SIGUSR2`, `SIG_DFL`, `SIG_IGN`.

## Control Flow

The compiled test enters `main`, prepares deterministic arguments or fixtures, invokes the target libc/syscall wrapper directly or through local helpers, and prints expected strace lines ending in `+++ exited with 0 +++`. Local helpers such as `handle_signal`, `main` split setup, syscall invocation, and expected-output formatting.

## State and Persistence Behavior

State is limited to local buffers, temporary descriptors, signal masks/handlers, child-process status, and the printed trace transcript consumed by the strace harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

kernel-version and architecture availability can change errno values, supported flags, struct sizes, or skip behavior; signal timing and restart behavior must remain deterministic enough for golden-output comparison.

## Test Signals

successful build or harness interpretation, matching generated stdout/stderr against the expected strace transcript, and the canonical `+++ exited with 0 +++` marker when applicable.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/rt_sigaction.c -->
