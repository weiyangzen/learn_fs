<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in corrupted`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for TIPC networking.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `rb_first_postorder, dump_stack, arch_local_irq_restore, show_regs_print_info, print_address_description, kasan_report, __asan_report_load8_noabort, tipc_group_join`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `corrupted`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in corrupted`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in corrupted`, flags `CORRUPTED=Y, PANICKED=Y`, 159 log lines, 0 explicit report lines, and 8970 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
marked corrupted, so parser changes must continue to distinguish real frames from truncated, interleaved, or printk-dropped output; panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; the title intentionally falls back to `corrupted`, which is a regression-sensitive signal for frame extraction failure.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in corrupted`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in corrupted`, and representative frames around `corrupted` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/154 -->
