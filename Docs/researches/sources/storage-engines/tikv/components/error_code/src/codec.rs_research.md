<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/codec.rs -->
# sources/storage-engines/tikv/components/error_code/src/codec.rs

Purpose: this module declares codec-layer error-code constants under `KV:Codec:`.

Important APIs and constants: it exports `IO`, `BAD_PADDING`, `KEY_LENGTH`, `KEY_NOT_FOUND`, `VALUE_LENGTH`, and `VALUE_META`, plus `ALL_ERROR_CODES`. These cover low-level byte encoding/decoding and key/value format issues.

Control flow and state: there is no executable control flow beyond the macro expansion. `ALL_ERROR_CODES` is lazily initialized for iteration.

Dependencies and integration points: codec and storage layers can attach these constants to decode failures. The generator binary includes this module when producing `etc/error_code.toml`.

Risks: empty descriptions and workarounds reduce the usefulness of catalog output. The module does not implement `ErrorCodeExt` for any concrete codec error type, so mapping consistency depends on external code.

Test signals: no local tests exist; macro expansion is indirectly tested by `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/error_code/src/codec.rs -->
