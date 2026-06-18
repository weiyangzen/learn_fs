<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.awk -->
# sources/test-tools/strace/tests/fork--pidns-translation.awk

## Purpose
Covers AWK matching logic for `fork--pidns-translation` strace output. Source read: 15 lines, 283 bytes.

## Important APIs, Types, And Functions
includes/imports: none; defines: none; AWK rules: /fork/ {, match($0, "([0-9]+) in strace\x27s PID NS", a);, if (a[1]), fork_pid = a[1], }, /exited with 0/ {, if (!exit_pid), exit_pid = $1.

## Control Flow
AWK control flow evaluates each strace output record, applies regex substitutions/matches, and exits nonzero when a required pid-namespace translation pattern is absent or malformed.

## State And Persistence Behavior
No persistent state is written. AWK state is per-record variables and exit status while validating a trace log stream.

## Dependencies And Integration Points
Depends on only the C library/shell runtime and local test harness. Integrated by the strace tests Makefile/generated `.gen.test` scripts as a decoder or harness regression input.

## Risks And Test Signals
Risks: concurrency and process ordering can make trace matching fragile. Test signals: AWK exit status validates transformed trace output.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/fork--pidns-translation.awk -->
