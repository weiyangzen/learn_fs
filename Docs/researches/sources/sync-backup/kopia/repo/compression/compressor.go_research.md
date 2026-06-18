# sources/sync-backup/kopia/repo/compression/compressor.go

Purpose: central registry and common header handling for Kopia content compressors.

Important APIs/types/functions: `Name`, `Compressor`, global maps `ByHeaderID`, `ByName`, `HeaderIDToName`, `IsDeprecated`, and `isUnsupported`; registration helpers; `compressionHeader`; `DecompressByHeader`; `IsSupported`; `verifyCompressionHeader`; and `mustSucceed`.

Control flow: compressors register during package init. Registration panics on duplicate header IDs or names. Compression implementations write a four-byte big-endian header; decompression either dispatches by header or verifies a known header before decoding. Unsupported compressors can be registered for name/ID recognition while `IsSupported` returns false.

State and persistence behavior: global registry maps are process-wide and determine how persisted compression headers are interpreted. The four-byte header is stored in compressed content.

Dependencies/integration: used by content read/write managers and compressor implementations; depends on `internal/impossible` for panic-on-impossible errors.

Risks and edge cases: global mutable maps are not synchronized after init, so registration should remain init-time. Duplicate IDs/names panic. Header mismatch errors are security/format critical because they prevent decoding with the wrong algorithm.

Test signals: `compressor_test.go` verifies all supported compressors round-trip, compress zeros, generally do not compress random data, and cannot decode each other's headers.
