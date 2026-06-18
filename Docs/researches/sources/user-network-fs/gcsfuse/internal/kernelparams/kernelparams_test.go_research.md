## sources/user-network-fs/gcsfuse/internal/kernelparams/kernelparams_test.go

### Purpose
`kernelparams_test.go` validates the kernel parameter manager's filesystem, serialization, mapping, and safety behaviors.

### Important APIs, Types, And Functions
Tests target `atomicFileWrite`, `getDeviceMajorMinor`, `PathForParam`, all `Set*` methods, `ApplyGKE`, `writeValue`, and `ShouldUpdateMaxPagesLimit`. The suite replaces `readMaxPagesLimitFunc` to test host-limit decisions deterministically.

### Control Flow
The tests create temp files/directories for atomic writes and direct writes, skip Linux-only checks on other OSes, verify path strings for all known `ParamName` values, write a JSON GKE file and unmarshal it, and simulate current max-pages limits through a function override.

### State, Persistence, And Dependencies
Persistent test state is limited to temp directories. Some tests interact with OS permissions and may attempt a sudo fallback when a read-only file triggers permission denial. Dependencies are `testing`, `assert`, `os`, `filepath`, `runtime`, and JSON decoding.

### Integration Points
The tests ensure the manager emits a CSI-driver-readable config and resolves sysfs/procfs paths consistently with production code. Linux skips keep the suite portable while still testing platform-specific paths when possible.

### Risks
`TestWriteValue_PermissionDenied_SudoFallback` is environment-dependent and can pass either via successful sudo or an expected sudo error. It does not assert no sudo is attempted in restricted CI beyond error content. Direct `ApplyNonGKE` is not exercised against real FUSE mount points.

### Test Signals
Signals are good for schema shape, setter validation, parameter replacement, no-op empty apply, path mapping, and max-pages safety logic. Missing signals include concurrent manager mutation and end-to-end CSI consumption.
