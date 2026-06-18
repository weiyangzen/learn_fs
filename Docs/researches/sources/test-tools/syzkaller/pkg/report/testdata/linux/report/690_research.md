# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/690

## Purpose

This file is a syzkaller Linux report-parser fixture, not executable production code. It feeds `pkg/report` a captured console log and an expected header contract so `report_test.go` can verify Linux crash detection, title extraction, alternate-title generation, crash-type classification, corruption detection, panic detection, and report slicing. KMSAN kernel-infoleak through skb datagram iterator, keeping `__skb_datagram_iter` as the selected frame.

## Important APIs, Types, and Functions

The fixture is consumed by `parseReport`, `parseHeaderLine`, `testParseImpl`, and `testFromReport` in `sources/test-tools/syzkaller/pkg/report/report_test.go`. Runtime parsing is handled through `Reporter.Parse`, `Reporter.ParseFrom`, `Reporter.ContainsCrash`, and the Linux implementation in `linux.Parse`, `findFirstOops`, `findReport`, `extractDescription`, `isCorrupted`, and `crash.TitleToType`. The source file itself exposes no functions or types; its stable API is the header schema (`TITLE`, `ALT`, `TYPE`, `PANICKED`, `CORRUPTED`, optional `REPORT`) plus the raw log bytes after the first blank line.

## Control Flow

`parseReport` reads the whole file, removes carriage returns, parses header lines until the first blank line, and passes the remaining log to the Linux reporter. `testParseImpl` expects `ContainsCrash` to agree with whether a title was declared, then compares the parsed `Report` fields with the headers and optional report body. Expected parser contract: title `KMSAN: kernel-infoleak in __skb_datagram_iter`, type `KMSAN-INFO-LEAK`, alternate titles `bad-access in __skb_datagram_iter`, `Panicked=N`, and `Corrupted=N`. The first notable signal line in the body is `[ 2104.503364][ T4311] BUG: KMSAN: kernel-infoleak in _copy_to_iter+0x870/0x1fd0`. There is no explicit `REPORT:` block, so the expected report body is whatever the Linux parser extracts from the console log.

## State and Persistence Behavior

The fixture has no mutable runtime state and no persistence side effects. Its only state is textual: 57 lines and 3061 bytes of headers plus console output. Header order, blank-line placement, timestamps, task contexts, architecture-specific frame formatting, and panic/corruption markers are significant because the test harness derives start, end, title, and body expectations from the exact byte stream.

## Dependencies and Integration Points

This file integrates with the generic report test runner that scans `pkg/report/testdata/linux/report`. It depends on the Linux oops pattern table, sanitizer-specific title rules, dynamic-title replacement in `report.go`, and crash type mapping in `pkg/report/crash`. It is indirectly exercised by `go test ./pkg/report`, fuzzing through `fuzz.go`, and any automation that regenerates report fixtures with `-update`.

## Risks

The main risk is parser drift: broadening Linux oops regexes can turn negative fixtures into crashes, while changing stack-frame preference can alter the selected function in positive fixtures. Sanitizer logs often contain helper frames before the actionable frame, and panic or secondary-oops text can appear after the primary report. Editing timestamps or trimming lines can also change `StartPos`, `EndPos`, corruption status, or the optional exact report comparison.

## Test Signals

Useful signals are a passing `TestParse` for this fixture, agreement between `ContainsCrash` and `Parse`, preserved alternate-title ordering after sorting, stable `Panicked` and `Corrupted` flags, and no unintended change to the exact report bytes when a `REPORT:` block is present.
