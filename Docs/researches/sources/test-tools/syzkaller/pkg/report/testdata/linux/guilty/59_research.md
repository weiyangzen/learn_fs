<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59

Purpose: This fixture validates Linux guilty-file extraction for a soft lockup report. The expected `FILE` header is `kernel/smp.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `3211` bytes across `56` lines, with content hash prefix `e836602706d2` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `exit_to_kernel_mode`, `el1_interrupt`, `_stext`, `____do_softirq`, `smp_call_function_many_cond`, `on_each_cpu_cond_mask`; source-path cues include `kernel/smp.c`, `arch/arm64/kernel/entry-common.c`, `arch/arm64/kernel/irq.c`, `arch/arm64/include/asm/cmpxchg.h`, `include/linux/smp.h`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `watchdog: BUG: soft lockup - CPU#1 stuck for 23s! [syz-executor.2:3705]`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `kernel/smp.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: kernel/smp.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/59 -->
