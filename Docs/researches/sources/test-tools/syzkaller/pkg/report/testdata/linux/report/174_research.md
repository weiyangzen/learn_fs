<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174

## Purpose
This is a syzkaller Linux report-parser fixture for `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174` so `pkg/report` can verify null-pointer page-fault coverage with a stable bad-access alternative title for rtnetlink interface dump.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `strlen, rtnl_fill_ifinfo, rtnl_dump_ifinfo, netlink_dump, __netlink_dump_start, rtnetlink_rcv_msg, rtnl_getlink, validate_linkmsg`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `rtnl_dump_ifinfo`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`, type `NULL-POINTER-DEREFERENCE`, alternatives `bad-access in rtnl_dump_ifinfo`, flags `PANICKED=Y`, 70 log lines, 0 explicit report lines, and 5009 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `BUG: unable to handle kernel NULL pointer dereference in rtnl_dump_ifinfo`, the crash type remains `NULL-POINTER-DEREFERENCE`, alt titles remain `bad-access in rtnl_dump_ifinfo`, and representative frames around `rtnl_dump_ifinfo` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/174 -->
