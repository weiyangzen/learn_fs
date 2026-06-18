<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342

## Purpose
This is another minimal corrupted warning fixture with panic-on-warn. It protects fallback behavior for short warning excerpts.

## Important APIs, Types, And Functions
The body contains a warning line and panic-on-warn context but not enough reliable stack detail for a stable function-specific title. The expected type is `WARNING`.

## Control Flow
The parser reads the generic warning, applies corrupted fallback title logic, and sets the panicked flag from the following kernel panic line.

## State And Persistence
The persistent oracle is `TITLE: WARNING in corrupted`, `TYPE: WARNING`, `CORRUPTED: Y`, and `PANICKED: Y`.

## Dependencies And Integration Points
This depends on warning regex coverage and corrupted report heuristics in the Linux reporter.

## Risks
Small formatting changes in warning detection can make short corrupted warnings disappear or become over-attributed.

## Test Signals
Expected output is exactly `WARNING in corrupted` with type `WARNING` and both flags set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/342 -->
