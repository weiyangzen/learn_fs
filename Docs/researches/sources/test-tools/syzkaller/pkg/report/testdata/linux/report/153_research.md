<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: kmalloc bug in relay_open_buf`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153` so `pkg/report` can verify WARNING and panic_on_warn coverage, where the primary warning stack must be kept while secondary panic stacks are trimmed or tolerated for relayfs buffer allocation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `kmalloc_slab, dump_stack, arch_local_irq_restore, vsnprintf, panic, refcount_error_report, show_regs_print_info, __warn`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `relay_open_buf`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: kmalloc bug in relay_open_buf`, type `WARNING`, alternatives `none`, flags `PANICKED=Y`, 86 log lines, 0 explicit report lines, and 4478 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report; warning stacks may be followed by panic stacks and unrelated device logs.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: kmalloc bug in relay_open_buf`, the crash type remains `WARNING`, alt titles remain `none`, and representative frames around `relay_open_buf` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/153 -->
