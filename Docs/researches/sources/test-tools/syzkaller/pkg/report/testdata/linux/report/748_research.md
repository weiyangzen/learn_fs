# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/748`. It records expected title `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref`; primary frame `<rust_binder::process::Process>::update_ref`. The raw log targets Rust Binder and gives the Linux reporter a concrete stack/signature to normalize into syzkaller crash metadata. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the positive parser path where `Reporter.Parse` must reproduce the embedded header oracle: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref`, type `none`, frame `<rust_binder::process::Process>::update_ref`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- `rust_helper_BUG`
- `_RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `__cfi__RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `_RNvMs0_NtCshgDM7dBCdno_11rust_binder4nodeNtB5_4Node22update_refcount_locked`
- `__cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel`
- `__cfi__RNvMs0_NtCshgDM7dBCdno_11rust_binder4nodeNtB5_4Node22update_refcount_locked`
- `__kasan_check_write`
- `_raw_spin_lock`
- `__cfi__raw_spin_lock`
- `_RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `__cfi__RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `_RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_sub_overflow`

## Control Flow

The test harness parses the header block into `ParseTest`, then passes the log body to `Reporter.Parse`. The Linux implementation should match the first oops-class line, collect same-context report text with `findReport`, derive `attempt to subtract with overflow in <rust_binder::process::Process>::update_ref` through `extractDescription`, map it through `crash.TitleToType`, and preserve the expected alternate titles, frame, panic, corruption, suppression, and executor fields. The log contains 142 lines and about 11576 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- rust_kernel: panicked at drivers/android/binder/node.rs:877:13:
- kernel BUG at rust/helpers/bug.c:7!
- Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Rust Binder functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses title normalization, stack-frame selection, and report-boundary detection with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
