<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/cloud.rs -->
# sources/storage-engines/tikv/components/error_code/src/cloud.rs

Purpose: this module declares cloud-storage related error codes under `KV:Cloud:` for object-store, encryption-key, and API failures.

Important APIs and constants: exported constants include `IO`, `SSL`, `PROTO`, `UNKNOWN`, `TIMEOUT`, `INVALID_INPUT`, `API_INTERNAL`, `API_NOT_FOUND`, `API_AUTHENTICATION`, `WRONG_MASTER_KEY`, and `BOTH_MASTER_KEY_FAIL`. `ALL_ERROR_CODES` is generated for catalog iteration.

Control flow and state: the module is pure declarations. Runtime state is limited to the lazy vector of constants. There is no conversion trait implementation in this file, so callers must choose constants manually or through wrappers in cloud-related crates.

Dependencies and integration points: the constants are consumed by cloud/external-storage/encryption error handling paths that need stable code strings for logging, metrics, or user-facing responses. `bin.rs` includes this module in generated catalog output.

Risks: descriptions and workarounds are empty, so the generated catalog contains only codes. Cloud backends often have provider-specific error classes, but this file keeps a coarse set of buckets; misclassification can make support diagnosis harder.

Test signals: no direct tests exist. Coverage comes from crate compilation and downstream consumers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/cloud.rs -->
