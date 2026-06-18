## sources/object-store/rustfs/crates/targets/src/runtime/sidecar_protocol.rs

Purpose: defines the JSON-serializable handshake contract between the RustFS target runtime and an external sidecar plugin. The protocol version constant is `SIDECAR_RUNTIME_PROTOCOL_VERSION = "rustfs.target-runtime.v1"`, and the file models the minimum plugin capability surface as `SidecarPluginCapability::{HealthCheck, SendEvent, Shutdown}`.

Important APIs/types/functions: `SidecarHandshake` carries `protocol_version`, `plugin_id`, `plugin_version`, `supported_domains: Vec<TargetDomain>`, and `capabilities`. `SidecarHandshake::validate(expected_plugin_id)` enforces exact protocol version, exact plugin id, and presence of all three required capabilities. Serde `snake_case` renaming makes this the wire contract for sidecar IPC.

Control flow and state: validation is pure and stateless. It returns the first contract violation as a `String` error and otherwise `Ok(())`; it does not currently validate `supported_domains` against a caller requirement.

Dependencies and integration points: depends on `crate::TargetDomain` and serde. Sidecar launch/registration code should call `validate` after receiving a handshake before routing target events to the plugin.

Risks: all capabilities are mandatory, so adding a capability to the hard-coded loop would become a breaking protocol change. Error strings include expected and actual ids/versions, useful for operators but potentially noisy in logs. Domain support is advertised but not enforced here.

Test signals: unit tests cover accepting the expected contract and rejecting protocol mismatch. Missing tests include plugin id mismatch, missing capability, and domain filtering behavior.
