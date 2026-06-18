# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93

## Purpose

This source file is a Linux syzkaller report-parser fixture for `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/93` with no `TITLE` header. It covers negative camera driver informational boot lines and ensures the Linux reporter does not treat ordinary warnings, Android boot strings, or informational diagnostics as crashes.

## Important APIs, Types, and Functions

The important APIs and data types are `ParseTest`, `parseReport`, `parseHeaderLine`, `testParseImpl`, `Reporter.Parse`, the Linux reporter implementation, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, `setExecutorInfo`, and `crash.TitleToType`. Expected parser fields are: title `none`, type `none`, frame `none`, alternate titles none, flags `none`, executor `none`, and explicit report block `no`. Representative symbols or frames visible to the parser are:

- none observed in the compact fixture body

## Control Flow

The test harness still reads the file into `ParseTest`, but the missing `TITLE` is intentional. `Reporter.Parse` should scan the full log, fail to find a valid oops start, and return no report; the expected value is an empty parsed result rather than a low-confidence crash. The fixture has 4 total lines, 3 log lines, 0 expected report lines, and 260 bytes. Salient log lines include:

- [   16.761978] [syscamera][msm_companion_pll_init::526][BIN_INFO::0x0008]
- [   16.762666] [syscamera][msm_companion_pll_init::544][WAFER_INFO::0xcf80]
- [   16.763144] [syscamera][msm_companion_pll_init::594][BIN_INFO::0x0008][WAFER_INFO::0xcf80][voltage 0.775]

## State and Persistence Behavior

There is no mutable runtime state in this file. The durable state is the fixture text itself: header lines encode the oracle, the first blank line starts the console log, and an optional `REPORT:` section stores the expected extracted/symbolized report body. The reporter must not persist context between fixtures; otherwise a previous title, corruption decision, executor id, panic flag, or symbolization state could contaminate this case.

## Dependencies and Integration Points

Dependencies and integration points include Linux oops regexes, console prefix stripping, task/cpu context tracking, sanitizer and lockdep title extraction, `crash.Type` classification, syzkaller executor metadata parsing, optional report-body comparison, and `ContainsCrash`/fuzz consistency. Kernel-side dependencies are text-only: subsystem frames, sanitizer banners, lockdep/debugobjects/refcount wording, panic lines, audit or boot noise, and architecture register/trace formats.

## Risks and Edge Cases

The main risk is a false positive: broad warning or info regexes could turn benign console text into a crash.

## Test Signals

The key test signal is negative: `TestParse` should produce an empty parsed result. Any non-empty title, type, frame, report body, corruption marker, or panic flag indicates an over-broad Linux/NetBSD oops rule and would make benign logs look like actionable crashes.
