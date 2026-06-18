# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/759`. It records expected title `int3 in __pmd_alloc` and covers panic-on-int3 trap in __pmd_alloc during clone/copy_page_range. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `int3 in __pmd_alloc`, type `DoS`, frame `__pmd_alloc`, alternate titles none, flags `PANICKED`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `__pmd_alloc`
- `copy_page_range`
- `dup_mmap`
- `copy_process`
- `kernel_clone`
- `__do_sys_clone`
- `do_syscall_64`
- `entry_SYSCALL_64_after_hwframe`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 28 total lines, 23 log lines, 0 expected report lines, and 1686 bytes. Salient log lines include:

- [  150.665871][    C0] Oops: int3: 0000 [#1] SMP KASAN NOPTI
- [  150.666570][    C0] Kernel panic - not syncing: Fatal exception in interrupt

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata. Panic detection must set `Panicked=true` without starting a second independent report at the panic line.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
