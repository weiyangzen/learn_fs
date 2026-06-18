<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_all.sh -->
# sources/test-tools/strace/tests/qualify_personality_all.sh

## Purpose

`sources/test-tools/strace/tests/qualify_personality_all.sh` is shared shell logic for `--trace=all@personality` qualification tests in the strace tests tree. Source read: complete file, 91 lines, 1940 bytes, sha256 `2da01f17734d21e3`.

## Important APIs, Types, and Functions

Includes: none found. Compile-time macros: none found. Functions/helpers: none found. Direct syscall numbers: none found. Notable constants/xlats: none found.

## Control Flow

The script sources `init.sh`, validates a target personality, skips unsupported or all-matching cases, and for native-personality all-trace checks iterates `pure_executables.list`, running each program under strace and asserting that only the expected execve line appears.

## State and Persistence Behavior

No durable application state is owned here. Temporary harness files such as `$LOG`, `$OUT`, `$EXP`, process exit statuses, and environment variables carry state only for the current test run.

## Dependencies and Integration Points

the shell harness from `init.sh`, `$STRACE`, and generated `$LOG`/`$OUT`/`$EXP` files. Integration is through the strace tests make/harness matrix; this file either compiles as a test binary, is included by a variant wrapper, or is consumed as shell/fixture input for a named test.

## Risks and Edge Cases

Risks include architecture/personality detection drift, missing helper commands, environment-variable assumptions, and fragile skip/fail behavior under cross-architecture test runs.

## Test Signals

Test signals are explicit `skip_`/`fail_` paths, `match_diff`/`match_grep` comparisons, and successful execution under the architecture/personality matrix.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/qualify_personality_all.sh -->
