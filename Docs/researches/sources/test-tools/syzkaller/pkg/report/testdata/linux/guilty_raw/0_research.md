<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0

Purpose: This fixture validates `ReportToGuiltyFile` on an already prepared report title/body pair. The expected raw guilty target is `fs/kernfs/dir.c` for title `WARNING in kernfs_get (4)`. The source is `3932` bytes across `67` lines, with content hash prefix `2b00d2381246` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `kernfs_create_dir_ns`, `sysfs_create_dir_ns`, `kobject_add_internal`, `kobject_init_and_add`, `net_rx_queue_update_kobjects`, `netdev_register_kobject`; source-path cues include `fs/kernfs/dir.c`, `fs/sysfs/dir.c`, `lib/kobject.c`, `net/core/net-sysfs.c`, `net/core/dev.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `raw guilty-file fixture`, the key body signal begins with: `------------[ cut here ]------------`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `fs/kernfs/dir.c` after ignore-list filtering and deepest-path selection. Header summary: `TITLE: WARNING in kernfs_get (4); FILE: fs/kernfs/dir.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty_raw/0 -->
