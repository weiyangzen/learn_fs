<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/sched.in -->
# sources/test-tools/strace/tests/sched.in

## Purpose

`sources/test-tools/strace/tests/sched.in` is an input list of scheduler test names and strace argument-count options in the strace tests tree. Source read: complete file, 10 lines, 277 bytes, sha256 `689c6ae003e47af3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

There is no executable control flow. The harness reads each non-comment row as a test selector or option line and feeds it into the surrounding shell/test runner.

## State and Persistence Behavior

The file is static fixture data and stores no runtime state. Its only persistence effect is the checked-in input rows consumed by the test harness.

## Dependencies and Integration Points

the surrounding strace tests build and harness rules. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks are malformed rows, stale test names, or option changes that cause the harness to run the wrong executable or argument-count mode.

## Test Signals

Test signals are the harness accepting the fixture rows, invoking the referenced tests with the listed options, and producing no unexpected extra trace lines.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/sched.in -->
