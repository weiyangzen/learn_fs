# sources/object-store/rustfs/crates/kms/src/backends/mod.rs

## Purpose
`backends/mod.rs` defines the backend abstraction layer for KMS implementations and exposes the concrete backend modules: local, Vault KV2, and Vault Transit.

## Important APIs, Types, and Functions
`KmsClient` is the low-level async trait with operations for data-key generation, direct encrypt/decrypt, key lifecycle (`create_key`, `describe_key`, `list_keys`, enable/disable, schedule/cancel deletion, rotate), health checks, and backend info. `KmsBackend` is the simplified service-manager-facing trait with owned request/response DTOs for create, encrypt, decrypt, generate data key, describe, list, delete, cancel deletion, and health check. `BackendInfo` carries backend type, version, endpoint, healthy flag, and arbitrary metadata with builder `with_metadata`.

## Control Flow
Concrete backend modules implement one or both traits. The split allows internal KMS logic to use a richer client-style interface with operation context while higher-level APIs use request/response DTOs. Health checks differ by trait: `KmsClient::health_check` returns `Result<()>`, while `KmsBackend::health_check` returns `Result<bool>`.

## State and Persistence Behavior
The module owns no state. It defines contracts that let backends decide whether to store data locally, in Vault KV, in Vault Transit, and/or in memory.

## Dependencies and Integration Points
It depends on `async_trait`, `std::collections::HashMap`, crate `Result`, and `crate::types::*`. The service manager and encryption service rely on these traits to abstract backend-specific behavior.

## Risks and Edge Cases
The two traits expose overlapping but not identical semantics, which can lead to wrapper inconsistencies. For example, a backend can implement safer key-material preservation in `KmsBackend` while the lower-level `KmsClient` method has different behavior. Request/response type names from `crate::types` must remain distinct from similarly named API DTOs in `api_types.rs`.

## Test Signals
No tests are defined in this module. Trait behavior is tested through concrete backend unit tests and examples.
