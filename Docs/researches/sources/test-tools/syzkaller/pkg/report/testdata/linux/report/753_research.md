# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/753`. It records expected title `WARNING: ODEBUG bug in handle_softirqs` and covers debugobjects active timer warning in rose protocol softirq handling. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING: ODEBUG bug in handle_softirqs`, type `WARNING`, frame `handle_softirqs`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `rose_timer_expiry`
- `kfree`
- `call_timer_fn`
- `_raw_spin_unlock_irq`
- `lockdep_hardirqs_on`
- `__run_timer_base`
- `seqcount_lockdep_reader_access`
- `run_timer_softirq`
- `handle_softirqs`
- `__irq_exit_rcu`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 154 total lines, 150 log lines, 0 expected report lines, and 9325 bytes. Salient log lines include:

- [ 1448.582480][    C1] ODEBUG: free active (active state 0) object: ffff88807b3c4490 object type: timer_list hint: rose_t0timer_expiry+0x0/0x350
- [ 1448.582538][    C1] WARNING: lib/debugobjects.c:615 at 0x0, CPU#1: kworker/1:3/17677

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
