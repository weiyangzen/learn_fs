# sources/sync-backup/kopia/repo/manifest/serialized.go

Purpose: implements memory-conscious decoding for serialized manifest content JSON.

Important APIs/types/functions: `manifest`, `manifestEntry`, `decodeManifestArray`, `parseFields`, `decodeArray`, `expectDelimToken`, `stringToken`, and `errEOF`.

Control flow: the decoder manually consumes the root object, looks for a single case-insensitive `entries` field, skips other fields, decodes each entry into a slice, and validates expected delimiters. EOF is converted to a package error for clearer diagnostics.

State/persistence behavior: decodes persisted manifest content batches; no writes occur here.

Dependencies/integration: called after gzip decompression in `loadManifestContent`; depends on `encoding/json` token streaming.

Risks/test signals: unknown fields are skipped only at token-label level; if an unknown field has a complex value, failing to consume it could break future extension unless handled by decoder token flow. Tests cover good and bad serialized inputs and all-field population.
