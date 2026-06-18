# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/97`. It records expected title `kernel panic: panic_on_warn set` and covers panic_on_warn report with stack around kasan_end_report/panic. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `kernel panic: panic_on_warn set`, type `DoS`, frame `none`, alternate titles none, flags `CORRUPTED, PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `dump_stack`
- `arch_local_irq_restore`
- `kasan_end_report`
- `lock_downgrade`
- `__internal_add_timer`
- `panic`
- `__warn`
- `add_taint`
- `kasan_report`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 26 total lines, 21 log lines, 0 expected report lines, and 1259 bytes. Salient log lines include:

- [  238.128296] Kernel panic - not syncing: panic_on_warn set ...
- [  238.177023]  panic+0x1e4/0x417

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. The corruption marker is part of the oracle, so boundary detection and mixed/interleaved log handling must preserve `Corrupted=true`. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
