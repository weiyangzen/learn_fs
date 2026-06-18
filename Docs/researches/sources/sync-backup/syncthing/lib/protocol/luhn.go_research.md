## sources/sync-backup/syncthing/lib/protocol/luhn.go

Purpose: base32 check-character helper used by device ID formatting and validation.

Important APIs: `luhnBase32`, `codepoint32`, and `luhn32`.

Control flow and state: `codepoint32` maps base32 bytes to numeric values. `luhn32` computes a modified Luhn-like checksum over a string and returns a base32 check rune or an error for invalid input.

Dependencies and integration points: used by `deviceid.go` to create and verify human-readable device ID chunks.

Risks: algorithm is intentionally not standard Luhn; compatibility with historical Syncthing IDs is critical. Invalid character handling must remain strict.

Test signals: `luhn_test.go` covers checksum examples and invalid inputs.
