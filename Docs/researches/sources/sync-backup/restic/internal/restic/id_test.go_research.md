
# sources/sync-backup/restic/internal/restic/id_test.go

Purpose: tests ID parsing, equality, and JSON encoding/decoding.

`TestStrings` contains known SHA-256 outputs for sample strings. `TestID` parses IDs, checks equality, marshals to quoted full hex, unmarshals back, and compares values. `TestIDUnmarshal` exercises invalid quote/length cases and one valid full-length ID.

State is pure value data. Integration points are backend file naming, config/key/index JSON, and integrity verification. Risks covered include malformed ID acceptance, JSON length drift, and equality implementation regressions. The tests do not cover case normalization explicitly, but `hex.Decode` behavior is inherited by `ParseID`.
