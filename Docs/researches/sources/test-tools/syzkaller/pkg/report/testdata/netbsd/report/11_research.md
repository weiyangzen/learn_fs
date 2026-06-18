# sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11

## Purpose

This source file is a NetBSD syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/netbsd/report/11`. It records expected title `UBSan: Undefined behavior` and exercises NetBSD/BSD crash extraction over a NetBSD console report. The file is persistent test data, not executable code, and its header is the oracle that `pkg/report` must reproduce from the console log body.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `testParseImpl`, `Reporter.Parse`, `ctorBSD`, the NetBSD oops tables, BSD stack extraction, optional `bsd.symbolizeLine`, and `crash.TitleToType`. Expected parser fields are: title `UBSan: Undefined behavior`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness reads the header block into `ParseTest`, separates the log body at the first blank line, and calls `Reporter.Parse`. The reporter must find the first relevant oops line, collect the report with same-context boundary rules, derive the normalized title and frame, classify the title through `crash.TitleToType`, and set corruption, panic, suppression, executor, and alternate-title fields exactly as declared. The fixture has 3 total lines, 1 log lines, 0 expected report lines, and 219 bytes. Salient log lines include:

- [     1.000003] UBSan: Undefined Behavior in /media/k4iz3n/event1/kWork/src/sys/dev/acpi/acpica/OsdHardware.c:265:17, left shift of 255 by 24 places cannot be represented in type 'int'

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include the shared report test harness, NetBSD-specific oops patterns, BSD stack-line parsing, crash title normalization, optional symbolization regexes, and `targets.NetBSD` reporter construction. Kernel-side dependencies are represented as console text: NetBSD trap/panic syntax, KASAN/UBSan strings, syscall frames, register dumps, LWP tables, dump/reboot trailers, and subsystem paths such as `sysv_shm`, `pmap`, and ACPI.

## Risks and Edge Cases

A parser regression could change the normalized title, lose the selected frame, misclassify the crash type, or drop alternate titles/executor metadata.

## Test Signals

The key test signal is `TestParse`: the parsed `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, `Executor`, and optional report body must match the header oracle. Regressions usually show up as a different title, nil report, unexpected corruption/panic state, wrong crash type, or an extracted report that starts or ends on the wrong line.
