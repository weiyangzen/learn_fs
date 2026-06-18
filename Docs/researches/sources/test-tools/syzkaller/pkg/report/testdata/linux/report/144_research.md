<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144

## Purpose
This is a syzkaller Linux report-parser negative fixture containing only `ODEBUG: Out of memory. ODEBUG disabled`. It keeps a minimal console line under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144` so `pkg/report` can verify that this diagnostic alone is not promoted to a crash report with a synthesized title.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the absence of `TITLE`, `TYPE`, `CORRUPTED`, `PANICKED`, and `REPORT` headers in the schema consumed by `ParseTest` in `report_test.go`. The runtime APIs under test are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, and the Linux oops matcher; the expected result is effectively nil/no crash rather than a populated `Report`.

## Control Flow
`parseReport` sees no header block and treats the single ODEBUG line as raw log input. `testParseImpl` calls the Linux reporter, which scans for known oops signatures; this file asserts that the out-of-memory debugobjects notice by itself should not pass the first-oops filter or enter normal `findReport` extraction.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in lack of expected metadata: no title, no type, no alternative titles, no flags, one log line, zero explicit report lines, and a very small source footprint. That absence is the important state because adding a title would change the fixture from negative coverage to positive crash coverage.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog and ignore/suppression choices, plus the generic `TestParse`/`forEachFile("report", ...)` fixture walker. It integrates with the same Linux reporter selected by `NewReporter`, but exercises the no-report path instead of title, stack, and crash-type normalization.

## Risks
The main risk is over-broad ODEBUG matching: future parser changes could incorrectly treat this resource-exhaustion notice as a reportable warning. The opposite risk is weaker but still relevant: if Linux starts printing this line adjacent to real ODEBUG warnings, report-boundary logic must avoid using this fixture to suppress legitimate multi-line reports.

## Test Signals
Regression signal is that parsing this exact log produces no expected crash metadata and no explicit report bytes. A useful smoke check is that `report/144` remains a negative fixture while neighboring ODEBUG fixtures, such as release/free-active warnings with `TITLE` headers, continue to parse as normal warnings.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/144 -->
