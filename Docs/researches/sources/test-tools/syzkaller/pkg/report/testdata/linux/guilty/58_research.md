<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58 -->
# sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58

Purpose: This fixture validates Linux guilty-file extraction for a RCU stall/lockdep report. The expected `FILE` header is `net/core/devlink.c`, so `TestGuiltyFile` should parse the report, symbolize it, and leave `Report.GuiltyFile` at that path. The source is `4600` bytes across `79` lines, with content hash prefix `d05e072fce07` used here only as a read-verification signal.

Important APIs/types/functions: The consuming code is syzkaller `pkg/report` test infrastructure: `parseReport`, `parseHeaderLine`, `TestParse`, `TestGuiltyFile`, `TestRawGuiltyFile`, `Reporter.Parse`, `Reporter.Symbolize`, `ReportToGuiltyFile`, and Linux reporter logic in `extractGuiltyFileRaw`/`extractGuiltyFileImpl`. This fixture's visible stack/source cues include `sched_show_task`, `rcu_sched_clock_irq`, `update_process_times`, `tick_sched_handle`, `tick_sched_timer`, `__hrtimer_run_queues`; source-path cues include `net/core/devlink.c`, `kernel/sched/core.c`, `kernel/rcu/tree_stall.h`, `kernel/rcu/tree.c`, `kernel/time/timer.c`.

Control flow: The harness reads metadata lines until the first blank line, then treats the rest as the kernel log/report body. For this `guilty-file fixture`, the key body signal begins with: `rcu: INFO: rcu_preempt detected stalls on CPUs/tasks:`. The expected guilty file is derived from header/body matching rather than from any runtime state in the fixture itself.

State and persistence behavior: The file persists the expected guilty-file state in its `FILE` header and then stores a representative Linux report body. No mutable state is created; the regression surface is the deterministic mapping from report text to `net/core/devlink.c` after ignore-list filtering and deepest-path selection. Header summary: `FILE: net/core/devlink.c`.

Dependencies and integration points: The fixture depends on syzkaller's Linux oops pattern tables, console-prefix stripping, optional symbolization, guilty-file ignore rules for generic kernel helper paths, and crash type normalization in `pkg/report/crash`. Kernel paths/functions in the body integrate it with Linux subsystem-specific parsing without requiring a checked-out kernel tree.

Risks and test signals: the main risk is over-normalizing stack text and changing the expected title, type, frame, or guilty path. A passing test means the parsed title/type/frame/corruption fields or guilty-file value still matches this fixture exactly; failures usually indicate a Linux report-regex, stack-frame ranking, console-prefix, or generic-helper ignore-list regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/pkg/report/testdata/linux/guilty/58 -->
