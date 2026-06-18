<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52

Purpose: This fixture validates Linux guilty-file extraction for a Linux crash report report. The expected `FILE` header is `net/core/net_namespace.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `1962` bytes across `35` lines, with content hash prefix `08d382807dbc` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `cold`, `free_netdev`, `netdev_run_todo`, `default_device_exit_batch`, `ops_exit_list`, `cleanup_net`; source-path cues include `net/core/net_namespace.c`, `lib/ref_tracker.c`, `include/linux/spinlock.h`, `net/core/dev.c`, `kernel/workqueue.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/net_namespace.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/net_namespace.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/52 -->
