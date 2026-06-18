<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: task hung in synchronize_rcu`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for RCU grace-period synchronization.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `__schedule, __sched_text_start, lock_downgrade, lock_release, mark_held_locks, check_noncircular, trace_hardirqs_on, schedule`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `synchronize_rcu`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: task hung in synchronize_rcu`, type `HANG`, alternatives `INFO: task hung in synchronize_sched, hang in synchronize_rcu, hang in synchronize_sched`, flags `none`, 110 log lines, 0 explicit report lines, and 5604 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: task hung in synchronize_rcu`, the crash type remains `HANG`, alt titles remain `INFO: task hung in synchronize_sched, hang in synchronize_rcu, hang in synchronize_sched`, and representative frames around `synchronize_rcu` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/179 -->
