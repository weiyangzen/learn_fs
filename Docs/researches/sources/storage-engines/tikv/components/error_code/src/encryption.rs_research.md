<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/encryption.rs -->
# sources/storage-engines/tikv/components/error_code/src/encryption.rs

Purpose: this module declares encryption subsystem error codes under `KV:Encryption:`.

Important APIs and constants: it exports `ROCKS`, `IO`, `CRYPTER`, `PROTO`, `UNKNOWN_ENCRYPTION`, `WRONG_MASTER_KEY`, `BOTH_MASTER_KEY_FAIL`, and `PARSE_INCOMPLETE`, plus the generated `ALL_ERROR_CODES`. These represent storage-engine errors, filesystem errors, encryption algorithm/key failures, protocol serialization, unknown method, key mismatch, dual master-key failure, and incomplete tail-record parsing.

Control flow and state: it is declarative and has no conversion implementation. The only runtime allocation is the lazy vector of constants.

Dependencies and integration points: encryption code and cloud/external-storage code can use these constants when mapping encryption-related failures. The generator binary includes this namespace.

Risks: empty descriptions and workarounds limit diagnostics. Several key-related codes overlap with `KV:Cloud` constants; callers should choose the subsystem where the error originates to avoid ambiguous telemetry.

Test signals: no local tests exist. Macro expansion and constant availability are covered by crate compilation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/encryption.rs -->
