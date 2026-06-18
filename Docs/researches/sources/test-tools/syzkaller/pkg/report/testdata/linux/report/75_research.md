# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/75`. It records expected title `BUG: scheduling while atomic in pause` and covers atomic-sleep detection around pause/SyS_pause. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `BUG: scheduling while atomic in pause`, type `ATOMIC_SLEEP`, frame `none`, alternate titles `BUG: scheduling while atomic in SyS_pause`, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `__schedule_bug`
- `__schedule`
- `schedule`
- `SyS_pause`
- `tracesys_phase2`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 19 total lines, 15 log lines, 0 expected report lines, and 1101 bytes. Salient log lines include:

- [  185.479466] BUG: scheduling while atomic: syz-executor0/19425/0x00000000
- [  185.486365] INFO: lockdep is turned off.

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
