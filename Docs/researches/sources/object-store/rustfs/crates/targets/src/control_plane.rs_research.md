# sources/object-store/rustfs/crates/targets/src/control_plane.rs

## Purpose
Declarative control-plane model for target plugin installation, enablement, runtime status, and external plugin action planning. It does not execute installs or sidecars; it validates whether an action should be allowed and returns the resulting desired state.

## Important APIs, types, and functions
- State enums: `TargetPluginInstallState`, `TargetPluginEnableState`, `TargetPluginRuntimeState`, and `TargetPluginExternalAction`.
- State records: `TargetPluginRevision`, `TargetPluginInstallation`, `TargetPluginOperationalState`, and `TargetPluginExternalActionDecision`.
- Constructors: `builtin_target_plugin_installation`, `external_target_plugin_installation`, `failed_external_target_plugin_installation`, `rollback_target_plugin_installation`, and `builtin_target_plugin_operational_state`.
- Gates and policies: `TargetPluginExternalFlowGate`, `TargetPluginExternalFlowGateStatus`, and `TargetPluginInstallPolicy`.
- Action planner: `plan_external_target_plugin_action`; install validator: `validate_external_plugin_installation`.

## Control flow
`plan_external_target_plugin_action` first rejects non-external manifests and closed/disabled gates. It then routes by action: install validates provider, protocol, distribution metadata, artifact URL host/scheme, digest, signature, and provenance; enable and disable require an installed revision; rollback additionally requires a previous revision. Decisions return cloned or newly constructed state but perform no I/O.

## State and persistence behavior
All state is serializable in-memory metadata. Builtin plugins are represented as virtually installed revisions with source `builtin`; external plugins carry digest, artifact id, install time, and previous revision for rollback. Persistence of these records would be a caller responsibility.

## Dependencies and integration points
The file ties manifests to sidecar runtime policy. It uses marketplace manifest fields from `manifest.rs`, sidecar policy and safety checks from `runtime/sidecar.rs`, protocol version from `sidecar_protocol`, `url::Url` for artifact validation, and serde for admin/control-plane serialization.

## Risks and edge cases
Default external flow is disabled and requires a closed circuit breaker, sandbox, provenance, and allowed artifact host. The allowlist currently defaults to `plugins.example.test`, making it more of a scaffold than a production policy. Digest validation only checks hex shape and minimum length, not an actual downloaded artifact. Runtime state results are planned labels, not evidence from a running process.

## Test signals
Tests verify builtin revision modeling, operational state mapping, runtime label mapping, external revision and rollback metadata, failed install records, disabled default gates, builtin-manifest rejection, signature/provenance requirements, sandbox and circuit-breaker enforcement, action planning for install/disable/rollback, and allowed/disallowed install policy cases.
