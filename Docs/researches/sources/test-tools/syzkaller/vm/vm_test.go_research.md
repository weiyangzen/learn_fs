# sources/test-tools/syzkaller/vm/vm_test.go

Purpose: regression tests for the high-level VM monitor, synthetic crash conversion, diagnostics, output buffering, preemption handling, no-output detection, and VM type parsing.

Important APIs/types/functions: fake `testPool`, `testInstance`, registered `"test"` backend, `withTestRunOptionsDefaults`, table-driven `tests`, `TestMonitorExecution`, `TestNilChannelBlock`, `makeLinuxAMD64Futex`, `testMonitorExecution`, `TestVMType`, `TestExtractMultipleErrors`, and embedded Linux KASAN fixture constants.

Control flow: fake instances expose buffered output and error channels. Each table case drives those channels to model normal exit, unexpected exit, kernel crash, delayed crash, diagnostics producing crashes, direct diagnostic output, timeout, command error, no output, executed-program heartbeats, closed output channels, split lines, and preempted executor strings. `testMonitorExecution` runs the monitor with short tick periods and asserts expected reports, titles, output snippets, types, or errors.

State and persistence: all state is in memory plus temporary manager workdirs. The init function mutates global `vmimpl.WaitForOutputTimeout` to keep tests short.

Dependencies and integration: uses Linux/AMD64 target metadata, `report.NewReporter`, `crash` types, `testify`, and the real `vm.Create`/`Instance.Run` wrapper.

Risks: global timeout mutation can affect other tests in the same package; fake channels intentionally bypass real backend process behavior; expected output snippets are sensitive to report parser changes.

Test signals: strong coverage of monitor control-flow edge cases, including single early-finish callback invocation, avoiding nil-channel blocking, `proxyapp:*` type stripping, and returning two parsed reports from one output buffer.
