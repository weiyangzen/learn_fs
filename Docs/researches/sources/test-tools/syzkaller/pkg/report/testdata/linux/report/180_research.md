<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180

## Purpose
This syzkaller Linux report-parser fixture exercises a corrupted mixed crash log where the expected title is `BUG: unable to handle kernel paging request in corrupted`, with alternate title `bad-access in corrupted`, type `MEMORY_SAFETY_BUG`, and both `CORRUPTED` and `PANICKED` set. The log starts with a page-fault signature and then contains a stronger KASAN use-after-free in `rb_first_postorder`, followed by panic-on-warn and a later oops in `dst_release`. Its purpose is to ensure the parser can classify the report as corrupted instead of over-trusting later stack frames.

## Important APIs, Types, And Functions
This is data consumed by syzkaller's `pkg/report` tests rather than executable code. The important fixture API is the header contract: `TITLE`, `ALT`, `TYPE`, `CORRUPTED`, and `PANICKED`, followed by raw console output. Parser paths exercised include Linux oops matching, KASAN report parsing, corrupted-report heuristics, title sanitization, crash-type mapping, and panic detection. Kernel functions visible in the signal include `rb_first_postorder`, `tipc_group_join`, `tipc_setsockopt`, allocation and free stacks through `tipc_group_create` and `tipc_group_delete`, plus the trailing `dst_release`, `ip6_make_skb`, and `udpv6_sendmsg` oops.

## Control Flow
`parseReport` reads the headers up to the blank line and passes the remaining 165-line log to the Linux reporter. The reporter sees an early `BUG: unable to handle kernel paging request`, then a KASAN use-after-free with allocation and free provenance, and later an additional oops after `Kernel panic - not syncing`. The expected behavior is to keep the selected title anchored to the corrupted bad-access class rather than generating a precise TIPC or IPv6 title from a secondary crash.

## State And Persistence
The file has no mutable state; the persistent state is the checked-in expected metadata and raw crash text. The log includes dynamic addresses, PIDs, CPU ids, slab object addresses, and register dumps that should be treated as volatile. The source records panic state and corruption state explicitly so regressions in metadata extraction are visible.

## Dependencies And Integration Points
It integrates through the Linux report testdata loader, `Reporter.Parse`, Linux KASAN matchers, panic detection, and `crash.TitleToType` mapping. It also depends on parser rules that distinguish primary reports from noisy follow-on oopses and on normalization rules for unstable addresses and offsets.

## Risks
The main risk is selecting `KASAN: use-after-free in rb_first_postorder` or `general dst_release` as the title and losing the intended corrupted-page-fault classification. Another risk is panic detection latching to the later fatal exception while ignoring the earlier `panic_on_warn` line. Because the log contains allocation/free sections and two crash contexts, report-boundary logic is also exposed.

## Test Signals
Regression checks should confirm title `BUG: unable to handle kernel paging request in corrupted`, alt `bad-access in corrupted`, type `MEMORY_SAFETY_BUG`, `CORRUPTED: Y`, and `PANICKED: Y`. The parsed report should preserve the KASAN use-after-free and panic evidence without promoting the follow-on `dst_release` oops to the primary crash.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/180 -->
