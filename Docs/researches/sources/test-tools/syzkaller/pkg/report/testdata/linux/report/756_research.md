# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/756`. It records expected title `WARNING in ovl_stack_put` and covers overlayfs dentry/inode release warning via ovl_stack_put. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `WARNING in ovl_stack_put`, type `WARNING`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dput`
- `ovl_stack_put`
- `ovl_destroy_inode`
- `evict`
- `_raw_spin_unlock`
- `iput`
- `__dentry_kill`
- `shrink_kill`
- `shrink_dentry_list`
- `shrink_dcache_tree`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 76 total lines, 73 log lines, 0 expected report lines, and 5197 bytes. Salient log lines include:

- [  195.364985][ T5830] WARNING: fs/dcache.c:829 at fast_dput+0x334/0x430, CPU#1: syz-executor/5830

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
