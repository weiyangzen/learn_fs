# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/713`. It records expected title `kernel BUG in bch2_fs_recovery`; type `BUG`; primary frame `bch2_fs_recovery`. The raw log targets bcachefs recovery and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `kernel BUG in bch2_fs_recovery`, type `BUG`, frame `bch2_fs_recovery`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `__phys_addr`
- `__die_body`
- `die`
- `do_trap`
- `do_error_trap`
- `bch2_fs_recovery`
- `__pfx_do_error_trap`
- `handle_invalid_op`
- `exc_invalid_op`
- `asm_exc_invalid_op`
- `kfree`
- `mark_lock`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `kernel BUG in bch2_fs_recovery` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 89 lines and about 5630 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- kernel BUG at arch/x86/mm/physaddr.c:23!

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: bcachefs recovery functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
