## sources/sync-backup/syncthing/lib/protocol/luhn_test.go

Purpose: tests modified base32 Luhn checksum behavior.

Important tests: known input/check-character pairs verify checksum output, and invalid characters verify error paths.

Control flow and state: simple table-driven unit tests.

Dependencies and integration points: protects device ID validation compatibility.

Risks: narrow by design; broader device ID parsing is covered in `deviceid_test.go`.

Test signals: focused checksum regression coverage.
