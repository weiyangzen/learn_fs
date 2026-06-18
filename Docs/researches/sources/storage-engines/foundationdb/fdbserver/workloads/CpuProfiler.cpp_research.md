# sources/storage-engines/foundationdb/fdbserver/workloads/CpuProfiler.cpp

Purpose: Defines `CpuProfiler`, a tester workload that turns Flow CPU profiling on and off across selected cluster workers for a configured window.

Important APIs/types/functions: `CpuProfilerWorkload`, `updateProfiler`, `getWorkers`, `WorkerInterface`, `ProfilerRequest`, worker `clientInterface.profiler`, `timeoutError`, and `PerfMetric` integration. Options include `initialDelay`, `duration`, and a list of process-class `roles`.

Control flow: `setup` is a no-op. `start` waits `initialDelay`, enables profiling on client 0, optionally delays for `duration`, and disables profiling. If `duration <= 0`, `check` disables profiling instead. `updateProfiler(true)` discovers workers, filters by role, records `profilingWorkers`, sends enable requests with output filenames based on worker address, and marks `success=false` if any enable reply is absent.

State and persistence behavior: Runtime state is the selected worker list and success flag. The workload causes worker-side profiler files named like `ip.port.profile.bin` to be written outside FDB key-value state. There are no database mutations.

Dependencies/integration: It depends on tester `dbInfo`, worker discovery from `TesterInterface`, the worker profiler RPC, trace logging, and Flow profiler support on target processes.

Risks: Only client 0 does work, so multi-client runs depend on that client surviving. Role strings must match process-class text. Disable replies are not used to update `success`, so failures during shutdown are mostly trace-level. A 60 second timeout bounds enable/disable RPC hangs.

Test signals: `SignalProfilerOn`, `SignalProfilerOff`, `DoneSignalingProfiler`, generated profile files, and final `check()` returning `success`.
