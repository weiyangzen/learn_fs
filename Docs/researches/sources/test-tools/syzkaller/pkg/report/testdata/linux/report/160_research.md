<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel paging request in __run_timers`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160` so `pkg/report` can verify generic oops memory-safety coverage, where page-fault and NX traces are normalized into a stable bad-access title for timer-list callback execution.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `call_timer_fn, __run_timers, irq_exit, run_timer_softirq, timers_dead_cpu, __do_softirq, exiting_irq, smp_apic_timer_interrupt`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `__run_timers`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel paging request in __run_timers`, type `MEMORY_SAFETY_BUG`, alternatives `bad-access in __run_timers`, flags `PANICKED=Y`, 110 log lines, 0 explicit report lines, and 5921 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel paging request in __run_timers`, the crash type remains `MEMORY_SAFETY_BUG`, alt titles remain `bad-access in __run_timers`, and representative frames around `__run_timers` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/160 -->
