# sources/test-tools/syzkaller/pkg/manager/diff/repro.go

Purpose: Verifies patched-kernel reproducers against the base kernel to determine whether a crash is patch-specific or also affects the base.

Important APIs and types: `reproRunner` implements the internal `runner` interface with `Run` and `Results`. `reproRunnerResult` carries the patched repro report, optional base crash report, repro object, and whether the repro was a full repro. Constants `reliabilityCutOff` and `reliabilityThreshold` control how many base runs are required.

Control flow: `Run` skips reproducers below 40% reliability. Reproducers at or above 80% reliability run three times; lower but accepted reproducers run six times. For each run it reserves base VMs according to concurrent runner count, copies repro options, forces repeated execution, forces threaded mode two out of every three runs, then uses `instance.SetupExecProg` and `RunSyzProg`. Any base crash is enough to mark the bug as affecting base, regardless of exact title.

State and persistence: Maintains a `running` atomic counter to reserve VMs in the base dispatcher and emits results over a buffered `done` channel. It does not write artifacts; `diffContext.handleReproResult` updates store state.

Dependencies and integration: Uses `Kernel` for config/reporter/pool access, `instance` for execprog setup, `repro.Result` options/programs, and VM dispatcher pool execution.

Risks: Run errors do not increment `doneRuns`, so persistent VM/setup errors can loop until context cancellation. Accepting any base crash minimizes false patched-only reports but can hide title-specific differences. Reliability thresholds are policy constants with probabilistic assumptions.

Test signals: Diff manager tests mock this runner; direct VM behavior is not covered in this file’s tests.
