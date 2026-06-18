<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: slab-out-of-bounds Read in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15` so `pkg/report` can verify KASAN read violation coverage, including slab, stack, or bounds reports for parser corruption/truncation handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memcpy`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: slab-out-of-bounds Read in corrupted`, type `KASAN-READ`, alternatives `bad-access in corrupted`, flags `CORRUPTED=Y`, 5 log lines, 0 explicit report lines, and 474 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure; sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: slab-out-of-bounds Read in corrupted`, the crash type remains `KASAN-READ`, alt titles remain `bad-access in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/15 -->
