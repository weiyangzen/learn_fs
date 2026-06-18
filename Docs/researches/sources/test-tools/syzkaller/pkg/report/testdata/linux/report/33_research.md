<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33

## Purpose
This compact fixture verifies lockdep parsing for an inconsistent lock state in `inet_ehash_insert`. The expected title is `inconsistent lock state in inet_ehash_insert`, type `LOCKDEP`, with `CORRUPTED: Y`.

## Important APIs, Types, And Functions
The consumed API is the report fixture header schema plus a short lockdep body. The key runtime markers are `[ INFO: inconsistent lock state ]`, the transition text `inconsistent {IN-SOFTIRQ-W} -> {SOFTIRQ-ON-W} usage`, and the lock site `inet_ehash_insert+0x240/0xad0`.

## Control Flow
Parser control flow is minimal: metadata is read, the first lockdep banner is found, and the lock site is extracted from the `at:` clause. The fixture is short enough that report-boundary logic has little surrounding noise.

## State And Persistence
The fixture persists only expected title/type/corruption metadata and the raw kernel log. The corrupted flag records that this short excerpt is not a complete, clean lockdep report.

## Dependencies And Integration Points
It depends on Linux lockdep pattern recognition, stack/site extraction from lockdep prose, and crash type mapping to `LOCKDEP`. It integrates through syzkaller's generic `TestParse` testdata loop.

## Risks
Because the body is truncated, parser changes that require a complete lockdep dependency chain would break this regression.

## Test Signals
The parser should still select `inet_ehash_insert` as the title function and classify the report as `LOCKDEP` despite the short input.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/33 -->
