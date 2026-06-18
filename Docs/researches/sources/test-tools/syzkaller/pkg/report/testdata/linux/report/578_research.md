# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/578

## Purpose
Static Linux reporter parse fixture for syzkaller. It pins expected title `kernel BUG in free_netdev`, expected type `BUG`, and parser behavior for a KASAN memory-safety diagnostic using x86/GCE syzkaller console format, panic-on-warn trailer. The source is immutable kernel-console text plus expectation headers, not executable code; its purpose is to prevent regressions in Linux crash detection, title normalization, crash-type mapping, panic/corruption flags, and report-boundary extraction.

## Important APIs, Types, And Functions
The file is consumed by `pkg/report/report_test.go` through `parseReport`, `testParseImpl`, `Reporter.ContainsCrash`, `Reporter.Parse`, and `Reporter.ParseFrom`. Parsed expectations are represented by `ParseTest` fields such as `Title`, `AltTitles`, `Type`, `Corrupted`, `Panicked`, `HasReport`, and `Report`, then compared with `testFromReport` output and `pkg/report/crash.TitleToType`. It exercises kernel BUG recognizers, panic/oops boundary detection, and subsystem-specific frame choice from skbuff, filesystem, networking, or boot-time call traces. Parser-relevant local signals: key stack symbols include `__rtnl_newlink`, `rtnl_newlink`, `rtnetlink_rcv_msg`, `netlink_rcv_skb`, `netlink_unicast`, `netlink_sendmsg`, `sock_sendmsg`, `____sys_sendmsg`; expected panicked flag is `Y`. First non-header signal: `[  429.970583][T14786] ------------[ cut here ]------------`.

## Control Flow
Test execution enumerates `pkg/report/testdata/linux/report`, reads the header block until the blank line, treats the remaining text as the console log, and optionally separates an exact expected report body after a standalone `REPORT:` marker. For this fixture, `ContainsCrash` must return true and `Parse` must produce the expected report with stable title/type/flags, and `ParseFrom` must rediscover the same report at its start offset while rejecting offsets at/after the parsed end. The raw log has 61 lines and is intentionally stored under an opaque numeric filename so the header and transcript are the behavioral contract.

## State And Persistence Behavior
All persistent state is the text fixture itself: expectation headers, optional comments, console bytes, alternate titles, and optional `REPORT:` body. The test creates only transient parser state such as report start/end offsets, selected frame, panic/corruption booleans, crash type, executor metadata, and normalized report bytes. There is no filesystem, network, device, or kernel mutation by this file; kernel actions are represented only as historical log input.

## Dependencies And Integration Points
This fixture integrates with syzkaller's Linux reporter implementation in `linux.go`, generic report shaping in `report.go`, crash taxonomy in `pkg/report/crash`, and the fuzz/test invariants that require `ContainsCrash` and `Parse` to agree. Product integrations depending on this behavior include dashboard crash grouping, duplicate detection, repro triage, guilty-file/frame inference, bisection routing, and maintainer-facing report rendering. The fixture also protects Linux printk prefix stripping across task/CPU contexts and architecture-specific stack formats.

## Risks And Edge Cases
The main risk is parser overfitting: timestamps, task prefixes, helper frames, panic trailers, sanitizer helper functions, allocator wrappers, architecture register dumps, and noisy subsystem lines can all bias title extraction. Because this fixture expects a precise non-corrupted title, the parser must keep enough specificity to avoid merging unrelated crashes. Panic detection must remain attached to the original warning/oops instead of starting a second report. There is no explicit `REPORT:` body, so the test focuses on parsed metadata and report span consistency.

## Test Signals
A passing run of `go test ./pkg/report` for this fixture returns title `kernel BUG in free_netdev`, type `BUG`, alternate titles `none`, corrupted `N`, panicked `Y`, and exact-body comparison `no`. It must preserve the meaningful frame named by the expected title when one is available, avoid helper-only titles, maintain `Parse`/`ParseFrom` agreement, and avoid false positives on fixture text that is intentionally noisy or negative.
