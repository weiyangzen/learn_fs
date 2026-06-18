# sources/test-tools/syzkaller/pkg/manager/diff/kernel.go

Purpose: Implements one side of patch-diff fuzzing: a `kernelContext` that runs a manager RPC server, VM dispatcher, focused fuzzer, coverage filter setup, and crash extraction for either the base or patched kernel.

Important APIs and types: `kernelContext` implements the `Kernel` interface consumed by `diffContext` and `reproRunner`. `setup` builds the reporter, RPC server, VM pool, dispatcher, and report generator cache. Public interface methods expose crashes, triage progress, focus-area stats, coverage filters, config, pool, features, and reporter. RPC-manager callbacks include `MachineChecked`, `MaxSignal`, `BugFrames`, and `CoverageFilter`.

Control flow: `Loop` starts RPC listening, RPC serving, VM dispatcher looping, and boot-error draining under an errgroup. `MachineChecked` records executor features, validates enabled syscalls, creates either a local fuzzer source or injected queue source, and wraps it with default executor options. `setupFuzzer` creates a focused corpus, disables fault injection for reproducibility, pulls candidate seeds, filters disabled calls, feeds candidates, and periodically distributes coverage signal deltas. VM instances are handled by `fuzzerInstance` and `runInstance`, which forward RPC, copy the executor, run the executor in runner mode, stop fuzzing after early crash detection, and send the first report to `crashes`.

State and persistence: Uses atomic pointers for the current fuzzer and candidate counts, buffered crash channel, stored `features`, `coverFilters`, optional shared/duplicated queue sources, and HTTP atomic pointers. It does not persist directly; persistence is handled by manager stores reached through higher-level loops.

Dependencies and integration: Integrates `corpus`, `fuzzer`, `queue`, `rpcserver`, `signal`, `vminfo`, `vm/dispatcher`, `report`, and manager coverage helpers. HTTP integration publishes fuzzer, enabled syscalls, corpus, modules, report generator, and executor cover filters.

Risks: Candidate delivery blocks until `setupFuzzer` receives from `kc.candidates`; cancellation must be respected. Coverage filtering must be initialized before patched-coverage monitoring expects populated areas. The fuzzer pointer is nil until machine check completes, so triage progress must handle startup. Boot errors are logged and discarded, not reported as diff bugs.

Test signals: Indirectly covered by diff harness mocks rather than real VM tests. Behavior relies on package-level manager and VM tests elsewhere.
