## sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler.go

### Purpose
`cloud_profiler.go` starts Google Cloud Profiler based on gcsfuse configuration.

### Important APIs, Types, And Functions
`SetupCloudProfiler` delegates to `setupCloudProfiler` with `cloudprofiler.Start`. `startFunctionType` makes the profiler start function injectable for tests.

### Control Flow
If `mpc.Enabled` is false, setup returns nil without side effects. Otherwise it builds `cloudprofiler.Config` from service name, label, and individual profiling booleans. Config booleans invert gcsfuse enable flags where the Cloud Profiler API uses `No*Profiling` fields. It forces GC for allocation profiling, calls the start function, and logs success.

### State, Persistence, And Dependencies
State is held by the Cloud Profiler library after start. Output is external profiler telemetry. Dependencies include Cloud Profiler, config types, logger, and Google API options.

### Integration Points
This is part of observability startup and ties profiler service/version labels to gcsfuse release/configuration.

### Risks
The function assumes a non-nil config pointer. Cloud Profiler start errors propagate and may affect mount startup depending on caller policy. No client options are currently passed despite the function type accepting them.

### Test Signals
Tests cover disabled no-op, enabled config mapping, and start failure propagation. They do not verify actual Cloud Profiler integration.
