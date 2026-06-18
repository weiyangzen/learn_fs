# Research: sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6

## Purpose
This fixture is a Fuchsia `pkg/report` parser test case for `sources/test-tools/syzkaller/pkg/report/testdata/fuchsia/report/6`. It feeds raw Zircon, Starnix, or Fuchsia component output into `Reporter.Parse` via `TestParse` and expects the normalized title `KERNEL PANIC in corrupted`.
It has no explicit `REPORT:` block, so the harness derives the expected report text from parser output while still checking title/type/corruption metadata.

## Important APIs, Types, And Functions
- Exercised APIs/types: `report.ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `Reporter.ParseFrom`, `ContainsCrash`, `simpleLineParser`, `fuchsia.Parse`, `fuchsia.shortenReport`, `fuchsia.shortenStarnixPanicReport`, `fuchsia.symbolize`.
- Fixture metadata: TITLE=KERNEL PANIC in corrupted, CORRUPTED=Y, SUPPRESSED=Y.

## Control Flow
- The generic test loader reads the file, parses headers until the first blank line, and treats the remaining content as console output unless a blank-line-delimited `REPORT:` section supplies an exact expected report.
- `Reporter.Parse` delegates to the OS reporter, which scans for configured oops signatures, normalizes the title/type, computes `StartPos` and `EndPos`, and returns a `Report` that `testParseImpl` compares against fixture headers.
- Fuchsia-specific flow symbolically rewrites Zircon program counters when kernel objects are available, removes unrelated halt/build lines, and separately shortens Starnix panic stacks around frame-like lines.

## State And Persistence
- Static fixture only: 53 lines and 4530 bytes. It has no runtime state, persistence layer, network activity, or side effects beyond being read by Go tests.
- There is no embedded expected report block; persistence is the file content plus header expectations or paired `.out` file in the same testdata directory.

## Dependencies And Integration Points
- Depends on the Fuchsia reporter configuration in `fuchsia.go`, the shared report parser in `report.go`, and test harness parsing in `report_test.go`. Symbolization may depend on configured kernel object paths but the fixture remains useful without modifying external state.

## Risks And Edge Cases
- Fuchsia logs contain timestamp prefixes, split assert lines, unrelated halt/build noise, and sometimes no explicit `REPORT:` block; small parser changes can alter boundaries or title normalization.
- The fixture explicitly expects corruption handling, so relaxed stack validation could turn a suppressed corrupted report into a false positive.

## Test Signals
- Primary signal: expected title `KERNEL PANIC in corrupted`, expected suppression, expected corruption.
- Regression signal: `go test ./pkg/report -run TestParse` should continue to parse this file with matching title, report bytes, suppression/corruption flags, and `ParseFrom` start/end behavior.

## Source-Specific Observations
- First crash/log signal: `ZIRCON KERNEL PANIC`.
