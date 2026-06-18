<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251

## Purpose
This is a negative/noise fixture for perf NMI throttling output. It begins with a blank header section and contains only `INFO: NMI handler ... took too long ... lowering kernel.perf_event_max_sample_rate`, so the expected parsed report is empty.

## Important APIs, Types, and Functions
The important harness behavior is `parseReport` entering log mode immediately because the file starts with a blank line. Parser code under test is the Linux suppression list, particularly patterns for `INFO: NMI handler` and `(handler|interrupt).*took too long`.

## Control Flow
The test harness records no expected `TITLE` or type. `Reporter.Parse` scans the single INFO line and must suppress it as benign performance-throttling noise instead of creating a crash report.

## State and Persistence Behavior
The file persists a two-line raw log and no expected metadata. It has no mutable state.

## Dependencies and Integration Points
It depends on Linux report suppression regexes in `linux.go` and on `testFromReport(nil)` producing an empty `ParseTest` for comparison.

## Risks and Edge Cases
The line includes typo-like `peperf: interrupt` text and numeric threshold values, so overly narrow suppression patterns may regress and report it as a crash.

## Test Signals
Success is no parsed report: empty title, unknown type, no flags, and no report body.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/251 -->
