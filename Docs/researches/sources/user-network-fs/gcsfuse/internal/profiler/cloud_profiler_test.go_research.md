## sources/user-network-fs/gcsfuse/internal/profiler/cloud_profiler_test.go

### Purpose
`cloud_profiler_test.go` verifies Cloud Profiler startup gating and config translation without contacting the real profiler service.

### Important APIs, Types, And Functions
Tests call the injectable `setupCloudProfiler` with mock start functions. Cases are disabled, enabled success, and enabled start failure.

### Control Flow
The disabled test ensures the mock start is not called. The success test captures `cloudprofiler.Config` and checks service, version, mutex, CPU, heap, allocated heap, goroutine, and `AllocForceGC` values. The failure test returns an error from the mock start and expects it to propagate.

### State, Persistence, And Dependencies
State is local mock variables. Dependencies are Cloud Profiler config types, gcsfuse config, Google API options, and testify.

### Integration Points
The tests protect the mapping between user-facing config flags and Cloud Profiler's inverse `No*Profiling` fields.

### Risks
They do not validate logging or real authentication/project behavior. Nil config is not tested.

### Test Signals
Signals are good for the core decision and mapping logic.
