# sources/object-store/rustfs/crates/targets/src/runtime/sidecar.rs

## Purpose
Policy and state model for external sidecar plugin runtimes. It validates activation safety checks, tracks sidecar health/failures, handles domain/handshake checks, and models degradation back to builtin behavior after repeated failures.

## Important APIs, types, and functions
- `SidecarRuntimePolicy` controls whether external sidecars are allowed, sandbox/provenance requirements, max queue depth, operation timeout, failure threshold, and error redaction.
- `SidecarRuntimeSafetyChecks` reports sandbox, provenance, and queue-depth evidence.
- `SidecarRuntimePolicyError` classifies activation denials.
- `SidecarPluginRuntime` stores endpoint, handshake, health, failure count, degraded flag, and last error.
- Methods include `enable`, `enable_with_policy`, `mark_unhealthy`, `record_failure`, `record_failure_with_policy`, `send_with_timeout`, and `shutdown`.

## Control flow
Enablement validates the sidecar handshake against an expected plugin id, checks required domain support, then optionally enforces runtime policy against safety checks. Failure recording increments counters, marks unhealthy, optionally redacts details, and sets `degraded_to_builtin` once the default or policy threshold is reached. Timeout simulation records a failure if latency exceeds the supplied operation budget.

## State and persistence behavior
All runtime state is in-memory and serde-compatible for status reporting. It does not manage an actual process or connection; endpoint and handshake data represent the sidecar boundary declaratively.

## Dependencies and integration points
It depends on `TargetDomain`, `SidecarHandshake`, serde, durations, and `thiserror`. `control_plane.rs` embeds `SidecarRuntimePolicy` and `SidecarRuntimeSafetyChecks` in external flow gates.

## Risks and edge cases
`record_failure` uses the module default threshold, while `record_failure_with_policy` uses policy threshold and redaction. `send_with_timeout` uses the non-policy failure path, so policy redaction does not apply there. Activation proves only declared safety checks, not OS-level sandboxing or provenance verification itself.

## Test signals
Tests cover successful enablement, default policy rejection, sandbox/provenance/queue-depth enforcement, verified external activation, redacted failure details and threshold degradation, domain mismatch rejection, shutdown health state, default threshold degradation, and timeout error recording.
