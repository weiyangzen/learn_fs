<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: workqueue leaked lock or atomic in addrconf_dad_work`. It preserves a `truncated workqueue leaked lock` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: shortened ipv6_addrconf worker report that still has the key last-function and Workqueue lines but lacks a complete trailing stack.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, type `none recorded`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: BUG: workqueue leaked lock or atomic in addrconf_dad_work` plus the raw kernel log body. This file currently has 11 lines and 688 bytes. The expected flags are PANICKED=N, CORRUPTED=N; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected non-corrupted result is part of the contract; parser changes should not over-mark this clean report as interleaved or truncated. The panicked flag should remain unset even though the log may contain severe oops or sanitizer text without a kernel panic line. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `BUG: workqueue leaked lock or atomic in addrconf_dad_work`, crash type remains `none recorded`, alt titles remain `none`, panic/corruption flags remain PANICKED=N, CORRUPTED=N, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/212 -->
