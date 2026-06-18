## sources/user-network-fs/gcsfuse/internal/kernelparams/contract.go

### Purpose
`contract.go` defines the JSON schema shared between GCSFuse and the GKE GCSFuse CSI driver for zero-configuration kernel parameter handoff. Its comments explicitly classify JSON tag, field, type, and `ParamName` value changes as compatibility-sensitive.

### Important APIs, Types, And Functions
`ParamName` is a string enum with `MaxPagesLimit`, `TransparentHugePages`, `MaxReadAheadKb`, `MaxBackgroundRequests`, and `CongestionWindowThreshold`. `KernelParam` holds one name/value pair. `KernelParamsConfig` contains `RequestID`, `Timestamp`, and `Parameters`. `newKernelParamsConfig` creates a config with a UUID and RFC3339Nano timestamp.

### Control Flow
There is no complex runtime flow in this file. Construction is one shot: create a UUID string, format current time, and leave the parameter slice empty for `KernelParamsManager` to populate.

### State, Persistence, And Dependencies
The persistent contract is serialized JSON with stable tags `request_id`, `timestamp`, `parameters`, `name`, and `value`. Dependencies are `time` and `github.com/google/uuid`.

### Integration Points
`kernelparams.go` embeds this config in `KernelParamsManager`, writes it atomically for GKE environments, and applies it directly for non-GKE mounts. The CSI driver is an external consumer, so this file is an inter-process and cross-repository API boundary.

### Risks
The largest risk is backward-incompatible schema drift. Adding fields or constants is documented as safe, but changing existing JSON names or enum string values can break CSI driver parsing. Timestamp uses local `time.Now()` with RFC3339Nano, so consumers must accept nanosecond precision.

### Test Signals
Tests in `kernelparams_test.go` exercise serialized GKE output and parameter names indirectly. Contract-specific golden JSON or compatibility tests against CSI-side expectations would strengthen this boundary.
