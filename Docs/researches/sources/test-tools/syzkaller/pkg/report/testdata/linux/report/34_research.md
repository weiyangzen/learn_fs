<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34

## Purpose
This short fixture verifies suspicious RCU usage detection when the report is corrupted or truncated. The expected title is `INFO: suspicious RCU usage in corrupted`.

## Important APIs, Types, And Functions
The key marker is `[ INFO: suspicious RCU usage. ]`. There are no complete stacks in this very small sample, so the parser's API contract is mostly header recognition and corrupted-title generation.

## Control Flow
The reporter reads the metadata, finds the RCU info banner, and cannot derive a reliable function. It therefore uses `corrupted` as the title function.

## State And Persistence
Persistent state is the expected title and `CORRUPTED: Y`. The fixture has no mutable state or explicit type header.

## Dependencies And Integration Points
It depends on RCU info pattern recognition and corruption heuristics in the Linux reporter.

## Risks
Requiring a full RCU splat would break this intentionally minimal regression.

## Test Signals
The stable parse is `INFO: suspicious RCU usage in corrupted` with corruption set.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/34 -->
