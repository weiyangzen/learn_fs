<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43

Purpose: This fixture validates Linux guilty-file extraction for a spinlock report. The expected `FILE` header is `net/netfilter/nf_conntrack_core.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `11678` bytes across `166` lines, with content hash prefix `ed60cd88f06b` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `nf_conntrack_locks`, `dump_stack`, `spin_dump`, `do_raw_spin_lock`, `_raw_spin_lock`, `nf_conntrack_lock`; source-path cues include `net/netfilter/nf_conntrack_core.c`, `lib/dump_stack.c`, `kernel/locking/spinlock_debug.c`, `include/linux/spinlock_api_smp.h`, `kernel/locking/spinlock.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `BUG: spinlock lockup suspected on CPU#1, kworker/u4:0/6`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/netfilter/nf_conntrack_core.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/netfilter/nf_conntrack_core.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/43 -->
