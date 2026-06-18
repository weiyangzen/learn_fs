<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: held lock freed in sctp_wait_for_sndbuf`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150` so `pkg/report` can verify lockdep and RCU/context validation coverage, where title extraction must preserve locking-context wording and the indicative kernel frame for SCTP socket lifetime and send-buffer handling.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `sctp_wait_for_sndbuf, dump_stack, arch_local_irq_restore, debug_check_no_locks_freed, kmem_cache_free, __sk_destruct, kasan_slab_free, sock_rfree`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `sctp_wait_for_sndbuf`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: held lock freed in sctp_wait_for_sndbuf`, type `LOCKDEP`, alternatives `none`, flags `none`, 86 log lines, 0 explicit report lines, and 4440 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
lockdep messages often contain unrelated subsystem chatter that can be mistaken for the first report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: held lock freed in sctp_wait_for_sndbuf`, the crash type remains `LOCKDEP`, alt titles remain `none`, and representative frames around `sctp_wait_for_sndbuf` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/150 -->
