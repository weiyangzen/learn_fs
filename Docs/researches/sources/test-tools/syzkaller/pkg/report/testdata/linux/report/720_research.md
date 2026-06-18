# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/720`. It records expected title `INFO: rcu detected stall in corrupted`; type `HANG`; alternate title(s) `stall in corrupted`; flags `CORRUPTED=Y`, `EXECUTOR=proc=2, id=737`. The raw log targets RCU scheduler/stall detection and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `INFO: rcu detected stall in corrupted`, type `HANG`, frame `none`, alternate titles `stall in corrupted`, and flags `CORRUPTED, EXECUTOR`. The principal kernel/user-space symbols visible to the parser are:

- `__schedule`
- `__kasan_check_write`
- `_raw_spin_lock_irqsave`
- `__pfx___schedule`
- `prb_read_valid`
- `__pfx_prb_read_valid`
- `preempt_schedule`
- `preempt_schedule_common`
- `__pfx_preempt_schedule`
- `console_trylock`
- `__pfx_console_trylock`
- `preempt_schedule_thunk`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `INFO: rcu detected stall in corrupted` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 215 lines and about 12628 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:
- rcu: Tasks blocked on level-0 rcu_node (CPUs 0-1): P9294/1:b..l
- rcu: (detected by 1, t=10002 jiffies, g=13073, q=1262 ncpus=2)
- rcu: rcu_preempt kthread starved for 10005 jiffies! g13073 f0x0 RCU_GP_WAIT_FQS(5) ->state=0x0 ->cpu=0
- rcu: Unless rcu_preempt kthread gets sufficient CPU time, OOM is now expected behavior.
- rcu: RCU grace-period kthread stack dump:
- rcu: Stack dump where RCU GP kthread last ran:

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: RCU scheduler/stall detection functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
