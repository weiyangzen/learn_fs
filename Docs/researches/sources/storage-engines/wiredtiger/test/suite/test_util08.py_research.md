# sources/storage-engines/wiredtiger/test/suite/test_util08.py

## Purpose
`test_util08.py` is a smoke test for the `wt copyright` utility command.

## Important APIs, Types, and Functions
The class defines `test_copyright` and uses `suite_subprocess.runWt(['copyright'])` with an output file.

## Control Flow
It runs the utility, reads `copyright.out`, and checks that the text contains the word "Copyright".

## State and Persistence Behavior
No database state is created or persisted. The only file state is the captured command output.

## Dependencies and Integration Points
Depends on the external `wt` binary being available through the test harness and producing copyright text.

## Risks and Edge Cases
The assertion is intentionally broad, so it catches total command failure but not detailed formatting regressions.

## Test Signals
The output file contains "Copyright".
