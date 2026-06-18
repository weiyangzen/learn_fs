<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `drivers/trusty/trusty.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1492` bytes across `26` lines, with content hash prefix `23b86b101805` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `trusty_std_call32`, `dump_backtrace`, `show_stack`, `dump_stack`, `panic`, `__warn`; source-path cues include `drivers/trusty/trusty.c`, `kernel/lib/trusty/ipc.c`, `arch/arm64/kernel/traps.c`, `lib/dump_stack.c`, `kernel/panic.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `trusty: app-mgmt-test-srv2: 146: Channel wait failed: 0(4)`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `drivers/trusty/trusty.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: drivers/trusty/trusty.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/42 -->
