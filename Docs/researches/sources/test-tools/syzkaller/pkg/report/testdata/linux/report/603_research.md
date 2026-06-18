# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/603

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `(no crash expected)`, expected type `UnknownType/no TYPE header`, and parser behavior for a negative/no-crash console fixture using standard Linux printk/oops format. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction. This is intentionally a no-crash fixture: it contains alarming words such as panic/status/warn in driver logs, but no expected `TITLE` header.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises the negative path: `ContainsCrash` must ignore noisy subsystem messages and `Parse` must return no report. Parser-relevant local signals: no alternate flags beyond the header; the raw console body is the parser input. First non-header signal: `[    3.576566] [drm:sde_dbg_init:3432] evtlog_status: enable:0, panic:1, dump:2`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return false, `Parse` must not produce a report, and `ParseFrom` must remain consistent with the no-crash result. The raw log has 4 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture is negative, any returned report is a false positive; the parser must distinguish ordinary driver status text from real oops signatures. The absence of an expected panic flag is also meaningful and should not be inferred from unrelated words unless the log has a real panic marker. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `(no crash expected)`, type `UnknownType/no TYPE header`, alternate titles `none`, corrupted `N`, panicked `N`, and exact-body comparison `no`. It must return no crash for this noisy non-oops console text, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
