<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25

## Purpose
This minimal fixture verifies that a malformed or too-short WARNING report is classified as corrupted. The expected title is `WARNING in corrupted`, type `WARNING`, and `CORRUPTED: Y`.

## Important APIs, Types, and Functions
The file uses `TITLE`, `TYPE`, and `CORRUPTED` headers followed by a single warning line at `genl_unbind+0x110/0x130`. Parser code under test includes generic WARNING matching, corruption detection for incomplete reports, and fallback title formatting.

## Control Flow
The harness reads the headers and passes one log line to the Linux reporter. The reporter can identify a warning signature but has no full call trace or report context, so it must preserve the warning type while marking the result corrupted and using the synthetic `corrupted` frame.

## State and Persistence Behavior
The file persists only the expected corrupted parse result and one printk line. It has no mutable state.

## Dependencies and Integration Points
It depends on generic Linux warning regexes, report-boundary validation, and `ParseTest` support for the `CORRUPTED` flag.

## Risks and Edge Cases
If the parser becomes too permissive it may emit `genl_unbind` as a normal warning, hiding truncated-report handling regressions. If it becomes too strict it may miss that the log is still a warning.

## Test Signals
A passing parse keeps `TYPE: WARNING`, marks `CORRUPTED: Y`, and returns title `WARNING in corrupted`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/25 -->
