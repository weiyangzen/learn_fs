# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/710`. It records no expected crash title. This boot-log fragment contains CPU vulnerability and mitigation warnings without a syzkaller crash oracle, so it exercises ignore handling for informational boot warnings. The file is data rather than executable code, but it is part of the parser test corpus and therefore defines expected behavior for `pkg/report`.

## Important APIs, Types, and Functions

The fixture is consumed by `TestParse` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. `parseReport` reads the header block into `ParseTest`, stores alternate titles in `AltTitles`, and passes the log body to the Linux `Reporter`. The production path under test is the negative parser path where `Reporter.Parse` should return no crash report, or at least should not synthesize a title from warning-like noise: `Reporter.Parse`, `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`.

Expected parser fields: title `none`, type `none`, frame `none`, alternate titles none, and flags `none`. The principal kernel/user-space symbols visible to the parser are:

- No stable kernel stack frame is expected from this fixture.

## Control Flow

The test harness loads the file, finds no `TITLE:` oracle in the header block, and then feeds the remaining log to the Linux reporter. The relevant control flow is `findFirstOops` scanning each prefixed line against `linuxOopses` and the ignore expressions; a successful result here would be a regression because the fixture is intended to stay below report threshold. The log contains 27 lines and about 1522 bytes; it is small enough for the unit test to read as a single buffer. Salient report lines include:

- Speculative Return Stack Overflow: IBPB-extending microcode not applied!
- Speculative Return Stack Overflow: WARNING: See https://kernel.org/doc/html/latest/admin-guide/hw-vuln/srso.html for mitigation options.
- Speculative Return Stack Overflow: WARNING: kernel not compiled with CPU_SRSO.
- Speculative Return Stack Overflow: Vulnerable: No microcode

## State and Persistence Behavior

There is no mutable runtime state in this fixture. The persistent state is the text file itself: the leading metadata block is the oracle, the blank line separates it from the raw console stream, and any trailing report body would be compared byte-for-byte when present. The reporter must not persist derived state between fixtures; otherwise titles, panic flags, or corruption decisions from neighboring files in `testdata/linux/report` could contaminate this case.

## Dependencies and Integration Points

This fixture integrates the Linux reporter with the shared report-test harness, the `crash.Type` classification package, architecture-specific stack parsing, sanitizer-specific description extraction, and syzkaller executor metadata parsing. Kernel-side dependencies are represented only as text: Linux crash-report parsing functions, sanitizer banners, panic lines, syslog prefixes, workqueue/task contexts, and architecture register dumps. It also contributes to fuzz stability because `pkg/report/fuzz.go` expects `ContainsCrash` and `Parse` to agree on the same kind of input.

## Risks and Edge Cases

Main risks are over-broad regexes, under-broad stack-frame extraction, and accidental changes to ignore lists. This fixture stresses negative matching and noisy warning suppression with mixed prefixes, sanitizer wording, architecture-specific frames, and optional panic/corruption metadata. For sanitizer reports, origin/allocation/free sections must not displace the selected crash frame. For warning-only or boot-noise fixtures, warning words inside ordinary logs must not create false positives.

## Test Signals

A passing test keeps the parsed output equal to the header oracle: `Title`, sorted `AltTitles`, `Type`, optional `Frame`, `Corrupted`, `Suppressed`, `Panicked`, and `Executor`. For no-title fixtures, the useful signal is that no report is produced from the log body. Regressions usually appear as a changed title, a lost `bad-access` alternate title, an unexpected `DoS`/`WARNING` classification, an incorrect panic flag, or a parser crash while scanning truncated and interleaved console lines.
