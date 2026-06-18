<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172

## Purpose
This is a syzkaller Linux report-parser fixture for `KASAN: stack-out-of-bounds Read in xfrm_selector_match`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172` so `pkg/report` can verify KASAN read violation coverage, including slab, stack, or bounds reports for xfrm policy/state selector matching.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `memcmp, dump_stack, arch_local_irq_restore, show_regs_print_info, find_held_lock, print_address_description, kasan_report, __asan_report_load1_noabort`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `xfrm_selector_match`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `KASAN: stack-out-of-bounds Read in xfrm_selector_match`, type `KASAN-READ`, alternatives `bad-access in xfrm_selector_match`, flags `none`, 190 log lines, 0 explicit report lines, and 20529 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
sanitizer details are noisy but allocation/free metadata and access direction must remain parseable.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `KASAN: stack-out-of-bounds Read in xfrm_selector_match`, the crash type remains `KASAN-READ`, alt titles remain `bad-access in xfrm_selector_match`, and representative frames around `xfrm_selector_match` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/172 -->
