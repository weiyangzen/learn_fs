<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171

## Purpose
This is a syzkaller Linux report-parser fixture for `INFO: rcu detected stall in snd_pcm_oss_write`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171` so `pkg/report` can verify hang/stall detection coverage, where the parser must recognize scheduler, hung-task, or RCU-stall reports without a normal oops footer for ALSA OSS PCM write path.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sched_show_task, print_other_cpu_stall, check_cpu_stall.isra.61, rcu_check_callbacks, update_process_times, tick_sched_handle, tick_sched_timer, __hrtimer_run_queues`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `snd_pcm_oss_write`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `INFO: rcu detected stall in snd_pcm_oss_write`, type `HANG`, alternatives `stall in snd_pcm_oss_write`, flags `none`, 42 log lines, 0 explicit report lines, and 2554 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
hang reports lack the usual oops boundary and depend on scheduler/RCU wording.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `INFO: rcu detected stall in snd_pcm_oss_write`, the crash type remains `HANG`, alt titles remain `stall in snd_pcm_oss_write`, and representative frames around `snd_pcm_oss_write` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/171 -->
