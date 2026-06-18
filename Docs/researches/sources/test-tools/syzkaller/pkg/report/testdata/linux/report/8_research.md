# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/8`. It records expected title `KASAN: use-after-free Read in snd_seq_queue_alloc` and covers KASAN snd_seq_queue_alloc use-after-free with explicit report block. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `KASAN: use-after-free Read in snd_seq_queue_alloc`, type `KASAN-USE-AFTER-FREE-READ`, frame `none`, alternate titles `bad-access in snd_seq_queue_alloc`, flags `CORRUPTED`, executor `none`, and explicit report block `yes`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 23 total lines, 10 log lines, 7 expected report lines, and 748 bytes. Salient log lines include:

- [   95.152992] BUG: KASAN: use-after-free in snd_seq_queue_alloc+0x670/0x690 at addr ffff8801d0c6b080

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Because the fixture has an explicit `REPORT:` block, report extraction must match the body text, not merely the header fields.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
