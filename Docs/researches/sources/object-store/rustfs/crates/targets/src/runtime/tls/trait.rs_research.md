## sources/object-store/rustfs/crates/targets/src/runtime/tls/trait.rs

Purpose: defines `ReloadableTargetTls`, the protocol a TLS-capable notification target must implement to participate in coordinated certificate hot reload.

Important APIs/types/functions: associated type `Material` is the rebuilt client/pool/connector object. `tls_input_set` declares watched TLS files. `build_tls_material` constructs a fresh material object from disk. `apply_tls_material(generation, material, mode)` atomically replaces the target's active state and must preserve old state on error. `validate_tls_files` is an optional async pre-check with a default no-op.

Control flow and state: the trait itself is stateless; it encodes the two-phase reload contract: build new material off the send path, apply it atomically, and let the coordinator publish only after apply succeeds.

Dependencies and integration points: depends on `TargetError`, `async_trait`, `Arc`, target generation, apply mode, and input set. Implemented by target types such as AMQP, SQL, webhook, or other outbound clients.

Risks: correctness depends heavily on implementors honoring the atomic apply contract. The coordinator cannot verify that a failed `apply_tls_material` left old state intact. `validate_tls_files` is optional, so target-specific validation gaps can remain.

Test signals: fake/mock implementations in adapter and coordinator tests validate expected call ordering and failure handling from the coordinator side.
