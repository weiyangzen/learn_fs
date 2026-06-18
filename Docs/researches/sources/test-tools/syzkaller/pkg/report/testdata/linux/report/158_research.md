<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158

## Purpose
This is a syzkaller Linux report-parser fixture for `WARNING: refcount bug in dev_activate`. It keeps a real or minimized console log under `sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158` so `pkg/report` can verify refcount_t warning coverage, where underflow or increment-on-zero text is mapped to a refcount crash type for network device activation.

## Important APIs, Types, And Functions
The fixture is data rather than executable code. Its public contract is the header schema consumed by `ParseTest` in `report_test.go`: `TITLE`, repeated `ALT`, `TYPE`, `CORRUPTED`, `SUPPRESSED`, `PANICKED`, and optional `REPORT`. The runtime APIs exercised are `Reporter.Parse`, Linux `Parse`, `findFirstOops`, `findReport`, `extractDescription`, `crash.TitleToType`, and `setExecutorInfo`; kernel frames of interest include `refcount_inc, dump_stack, arch_local_irq_restore, panic, __warn, show_regs_print_info, retint_kernel, report_bug`.

## Control Flow
`parseReport` reads headers until the first blank line, treats the remainder as raw kernel log, and optionally switches to expected-report mode after a blank line plus `REPORT:` sentinel. The Linux reporter scans line by line for the first matching oops signature, strips printk prefixes/context, builds a bounded report around `dev_activate`, derives title/type/alt titles, and records panic/corruption flags before `testParseImpl` compares expected and actual fields.

## State And Persistence
The fixture has no mutable runtime state. Persistent state is the checked-in expected metadata: title `WARNING: refcount bug in dev_activate`, type `REFCOUNT_WARNING`, alternatives `none`, flags `PANICKED=Y`, 113 log lines, 0 explicit report lines, and 10039 bytes of source data. Dynamic addresses, ages, CPU ids, and PIDs are normalized in headers where needed, for example `NUM` or `ADDR`.

## Dependencies And Integration Points
It depends on syzkaller's Linux oops regex catalog, crash-type mapping, title sanitization/dynamic replacement, and stack parsing rules, plus the Linux subsystem vocabulary in the log. Integration is through `TestParse`, `forEachFile("report", ...)`, and the Linux reporter selected by `NewReporter` for the test target.

## Risks
panic_on_warn/panic aftermath is present, so secondary panic stacks can obscure the root report.

## Test Signals
Regression signal is a stable parse of title, type, alt titles, frame/corruption/panic/suppression flags, and report boundaries from this exact log. For this file specifically, useful smoke checks are that the first recognized report remains `WARNING: refcount bug in dev_activate`, the crash type remains `REFCOUNT_WARNING`, alt titles remain `none`, and representative frames around `dev_activate` are not displaced by unrelated console noise. There is no explicit `REPORT:` block, so the test compares parsed metadata and parser-selected report text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/report/158 -->
