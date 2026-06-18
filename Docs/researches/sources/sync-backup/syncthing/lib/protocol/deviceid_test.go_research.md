## sources/sync-backup/syncthing/lib/protocol/deviceid_test.go

Purpose: validates device ID formatting, parsing, equality, short IDs, text marshaling, and rejection of invalid IDs.

Important tests: test cases use known device ID strings such as the model test IDs and malformed variants to check round-trips and error paths.

Control flow and state: table-driven parse/format assertions and mutation of strings/check digits to prove validation works.

Dependencies and integration points: protects user-facing device identity and config/protocol compatibility.

Risks: tests must preserve historical formatting examples; new accepted forms require explicit cases.

Test signals: high-value coverage for identity parsing and check digits.
