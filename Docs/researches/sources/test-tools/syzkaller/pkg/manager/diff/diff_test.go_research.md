# sources/test-tools/syzkaller/pkg/manager/diff/diff_test.go

Purpose: Provides the test harness for the patch-diff fuzzer package. It defines `testEnv`, mock kernels, mock repro runners, and repro callbacks used by `manager_test.go`.

Important APIs and types: `testEnv` owns `context`, `diffContext`, base/new `MockKernel`, and a completion channel. `newTestEnv` wires default `DiffFuzzerStore`, `PatchedOnly`, `BaseCrashes`, and a mock runner. `MockKernel` implements the package `Kernel` interface: `Loop`, `Crashes`, `TriageProgress`, `ProgsPerArea`, `CoverFilters`, `Config`, `Pool`, `Features`, and `Reporter`. `mockRunner` implements the internal `runner` interface, and `mockRepro`/`mockReproCallback` emulate `repro.Run`.

Control flow and state: Tests call `env.start()` to run `diffContext.Loop` in a goroutine, inject crash reports into `CrashesCh`, and use `waitForStatus` to poll `DiffFuzzerStore.List`. The new kernel is given a one-VM dispatcher and blank manager config, enough for repro loop construction without real VM boot.

Dependencies and integration points: Imports `flatrpc`, manager store/repro types, `mgrconfig`, `report`, `repro`, `prog/test`, and VM dispatcher. It decouples diff state-machine tests from real RPC servers and VMs while preserving the production interfaces.

Risks: Polling waits can hide race-sensitive failures until timeout. The mock dispatcher has minimal behavior, so it does not validate real VM reservation interactions. `ReporterVal` is often nil, which is acceptable in mocked paths but not representative of production repro execution.

Test signals: Establishes deterministic scaffolding for diff-fuzzer tests and validates that the package can be exercised through interfaces rather than concrete kernel contexts.
