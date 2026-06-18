<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: ODEBUG bug in corrupted`. It preserves a `ODEBUG warning corrupted by allocation-failure stack` console shape under `pkg/report/testdata/linux/report` so `TestParse` can verify that the Linux reporter extracts the expected crash title, crash type, alternative titles, panic state, and corruption state from real kernel output rather than from synthetic unit data.

## Important APIs, Types, And Functions
The file is data, not executable code. Its API surface is the fixture header contract consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, optional `FRAME`, and optional `REPORT`. At runtime the important code paths are `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, Linux oops matching, `extractDescription`, report boundary selection, frame extraction, and `crash.TitleToType`. The kernel symbols and report signatures that matter for this fixture are summarized by: free-active work_struct in process_one_req is corrupted by a concurrent vmalloc allocation failure and another CPU context.

## Control Flow
`parseReport` reads the metadata headers until the first blank line and treats the rest of `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218` as raw console log. The Linux reporter scans the log line by line for an oops signature, strips printk prefixes or architecture-specific stack notation, ignores report-start patterns that can appear inside another report, and builds the selected `Report`. `testParseImpl` then compares the parsed title `WARNING: ODEBUG bug in corrupted`, type `WARNING`, alt titles `none`, panic flag, corruption flag, executor information if present, and explicit report text if the file contains a `REPORT:` block.

## State And Persistence
There is no mutable runtime state in this fixture. The persistent state is the checked-in header block `TITLE: WARNING: ODEBUG bug in corrupted; TYPE: WARNING; CORRUPTED: Y; PANICKED: Y` plus the raw kernel log body. This file currently has 103 lines and 4966 bytes. The expected flags are PANICKED=Y, CORRUPTED=Y; alternatives are `none`. Addresses, PIDs, CPU ids, device names, or syscall details may be normalized by the reporter, but the source fixture itself keeps the original console text so boundary and corruption heuristics remain testable.

## Dependencies And Integration Points
The fixture depends on syzkaller's Linux oops regex catalog, warning/KASAN/lockdep/hung-task/RCU-stall recognizers, dynamic-title sanitization, architecture-specific stack parsing, and crash type mapping. It is integrated through `TestParse`, `forEachFile("report", ...)`, target-specific reporter construction, and the surrounding Linux reporter implementation in `linux.go`. Because it lives in `testdata/linux/report`, normal Go test discovery treats it as golden input for the parser rather than as a standalone test binary.

## Risks
Parser changes can regress this file by selecting a generic helper frame, choosing a later interleaved report, missing an unprefixed or truncated architecture-specific line, changing normalized title wording, or flipping panic/corruption state. The expected corrupted flag is part of the contract; parser changes must keep rejecting unreliable frame attribution. The panicked flag should be set from panic-on-warn, fatal exception, hung-task panic, or equivalent kernel panic text. The highest-risk edits are broad changes to Linux oops ordering, `reportStartIgnores`, stack-frame filtering, and title fallback rules.

## Test Signals
The primary signal is that `go test ./pkg/report` parses this fixture into exactly the recorded metadata. For this file, useful smoke checks are: `ContainsCrash` returns true, the first stable title remains `WARNING: ODEBUG bug in corrupted`, crash type remains `WARNING`, alt titles remain `none`, panic/corruption flags remain PANICKED=Y, CORRUPTED=Y, and the selected report still includes the kernel evidence described above. Absence of a `REPORT:` block means parser-selected report boundaries are indirectly checked through metadata and generated report comparison when tests are updated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/218 -->
