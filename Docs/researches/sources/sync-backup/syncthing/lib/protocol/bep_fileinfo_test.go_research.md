## sources/sync-backup/syncthing/lib/protocol/bep_fileinfo_test.go

Purpose: validates `FileInfo` local flags, equivalence logic, block sizing, block hash behavior, wire/database consistency, and platform metadata comparisons.

Important tests: `TestLocalFlagBits` verifies invalid flag transitions. `TestIsEquivalent` is a broad table of name/type/size/deletion/invalid/mtime/permissions/blocks/ownership/xattr cases with optional ignore settings. Additional tests in the file cover block size selection, empty-block hashes, file-info consistency, wire conversion, and platform data behavior.

Control flow and state: table-driven tests construct `FileInfo` values, mutate flags or platform fields, and compare results from methods such as `IsEquivalentOptional`, `BlocksEqual`, and conversion functions.

Dependencies and integration points: uses build flags for platform permission semantics and validates invariants relied on by scanner, database, and puller code.

Risks: test coverage is broad but must be kept in sync with BEP schema changes and new platform metadata fields.

Test signals: high-value regression coverage for one of the protocol package's most central data types.
