<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs -->
# sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs

Purpose: JSON compatibility layer for serialized `CryConfig`, including legacy field names and format-version validation.

Important APIs/types/functions: `DeserializationError` distinguishes too-old, too-new, invalid config, and JSON errors. `serialize` writes a `SerializableCryConfig` wrapper under `cryfs`. `deserialize` reads, checks format/migration markers, validates required fields, parses blocksize and filesystem id, then constructs `CryConfig`.

Control flow: `check_format_version` requires the stored version to equal current `FILESYSTEM_FORMAT_VERSION`; missing version is treated as 0.8 and too old. Migration flags `hasVersionNumbers` and `hasParentPointers` must be present and true for 0.10.

State and persistence: defines on-disk JSON field names before encryption, including string-encoded byte and client-id values for compatibility.

Dependencies/integration: uses serde, serde_with, `Byte`, `Version`, and `FilesystemId`.

Risks/test signals: TODOs request tests for errors and C++ JSON compatibility. One invalid-message path repeats "hasVersionNumbers" for parent-pointer failure, which may confuse diagnostics.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/cryfs-config/src/config/cryconfig/serialization.rs -->
