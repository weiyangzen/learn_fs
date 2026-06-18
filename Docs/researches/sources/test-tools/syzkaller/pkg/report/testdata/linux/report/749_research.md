# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/749`. It records expected title `attempt to add with overflow in <ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap` and covers Rust ashmem mmap overflow panic through the Android miscdevice path. The file is data rather than executable code, but it defines exact `pkg/report` behavior by pairing a metadata header with the raw kernel/user-space console text that the Linux reporter must normalize.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `attempt to add with overflow in <ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap`, type `none`, frame `<ashmem_rust::Ashmem as kernel::miscdevice::MiscDevice>::mmap`, alternate titles none, flags `none`, executor `proc=0, id=595`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- `_RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `__cfi__RNvCscSpY9Juk0HT_7___rustc17rust_begin_unwind`
- `kernel_text_address`
- `__cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel`
- `__cfi_stack_trace_consume_entry`
- `arch_stack_walk`
- `_RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `__cfi__RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt`
- `_RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_add_overflow`
- `__cfi__RNvNtNtCs9jEwPDbx20M_4core9panicking11panic_const24panic_const_add_overflow`

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 80 total lines, 76 log lines, 0 expected report lines, and 7291 bytes. Salient log lines include:

- [   60.002464][ T2148] rust_kernel: panicked at /syzkaller/managers/ci2-android-6-12-rust/kernel/rust/kernel/page_size_compat.rs:60:5:
- [   60.041680][ T2148] Oops: invalid opcode: 0000 [#1] PREEMPT SMP KASAN PTI
- [   60.173624][ T2148]  ? __cfi__RNvXs1b_NtCs9jEwPDbx20M_4core3fmtRNtNtNtB8_5panic10panic_info9PanicInfoNtB6_7Display3fmtCs43vyB533jt3_6kernel+0x10/0x10
- [   60.189785][ T2148]  _RNvNtCs9jEwPDbx20M_4core9panicking9panic_fmt+0x84/0x90

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
