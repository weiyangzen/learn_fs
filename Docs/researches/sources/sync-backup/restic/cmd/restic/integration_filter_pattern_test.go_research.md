# sources/sync-backup/restic/cmd/restic/integration_filter_pattern_test.go

Purpose: integration tests that invalid filter patterns are rejected consistently by backup and restore commands.

Important APIs/types/functions: `TestBackupFailsWhenUsingInvalidPatterns`; `TestBackupFailsWhenUsingInvalidPatternsFromFile`; `TestRestoreFailsWhenUsingInvalidPatterns`; `TestRestoreFailsWhenUsingInvalidPatternsFromFile`.

Control flow and state: tests initialize repos, pass invalid include/exclude glob patterns inline or via pattern files, call backup/restore helpers expecting failure, and compare exact fatal error strings for each flag variant, including case-insensitive flags.

Dependencies and integration points: uses filter option structs, backup and restore command paths, temp files, and test environment setup.

Risks: exact error string comparisons are intentionally strict but can require updates when validation wording changes. Restore pattern tests may fail before snapshot lookup/target validation because filter collection happens first.

Test signals: validates command-layer propagation of filter validation errors and correct attribution to the relevant flag.
