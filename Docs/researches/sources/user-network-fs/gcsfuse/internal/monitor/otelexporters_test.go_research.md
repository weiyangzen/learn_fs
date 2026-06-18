## sources/user-network-fs/gcsfuse/internal/monitor/otelexporters_test.go

### Purpose
`otelexporters_test.go` validates the defensive wrapper around the Cloud Monitoring metric exporter.

### Important APIs, Types, And Functions
`mockExporter` implements `metric.Exporter` methods with an injectable `exportFunc`. Tests are `TestPermissionAwareExporter_ExportSuccess`, `TestPermissionAwareExporter_ExportPermissionDenied`, and `TestPermissionAwareExporter_ExportOtherError`.

### Control Flow
The success test exports once and expects no disabled state. The PermissionDenied test makes the first export return a gRPC PermissionDenied status, expects the wrapper to return that error and set `disabled`, then verifies the next export is skipped with nil error. The other-error test verifies generic errors do not disable the exporter.

### State, Persistence, And Dependencies
State is the wrapper's atomic disabled flag and mock export function. Dependencies are OTel metric data, gRPC status/codes, and testify assertions.

### Integration Points
These tests protect production behavior intended to avoid repeated noisy Cloud Monitoring failures when a mount lacks IAM permissions.

### Risks
The tests do not assert `ForceFlush` behavior when disabled or the log line emitted on first disable. They also do not check concurrent export races around `CompareAndSwap`.

### Test Signals
Signals are focused and good for the main permission-denied circuit-breaker behavior.
