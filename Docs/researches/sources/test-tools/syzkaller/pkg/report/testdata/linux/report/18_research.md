<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: null-ptr-deref Read`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18` so `pkg/report` can verify KASAN null-pointer read coverage with intentionally sparse legacy output for Linux crash-report parsing.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `none reliably extracted from this short/corrupted log`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `none isolated`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: null-ptr-deref Read`, type `KASAN-NULL-POINTER-DEREFERENCE-READ`, alternatives `none`, flags `CORRUPTED=Y`, 5 log lines, 0 explicit report lines, and 307 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: null-ptr-deref Read`, the crash type remains `KASAN-NULL-POINTER-DEREFERENCE-READ`, alt titles remain `none`, and representative frames around `none isolated` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/18 -->
