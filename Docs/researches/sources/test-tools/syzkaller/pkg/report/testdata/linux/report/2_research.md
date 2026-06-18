<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2

## Purpose
This minimal fixture contains only `INFO: lockdep is turned off.` and no expected title header. Its purpose is negative coverage: the Linux reporter should not manufacture a crash report from a benign informational line.

## Important APIs, Types, And Functions
The fixture has no `TITLE` or `TYPE` metadata and no call trace. The relevant parser behavior is ignoring lockdep status noise when scanning kernel logs.

## Control Flow
The test harness reads a two-line file and passes the raw text to the reporter. The expected outcome is no crash title/report extraction, or whatever the surrounding test semantics define for headerless non-crash input.

## State And Persistence
The only persistent state is the checked-in informational line. There are no dynamic addresses, stacks, or flags.

## Dependencies And Integration Points
It integrates with `forEachFile("report", ...)` negative test coverage and Linux ignore-pattern logic for non-oops messages.

## Risks
Over-broad lockdep matching could treat this informational line as a lockdep bug. Headerless fixture handling must also avoid false expectations.

## Test Signals
The stable signal is absence of a parsed crash from `INFO: lockdep is turned off.`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/2 -->
