# sources/sync-backup/restic/internal/fs/stat.go

Purpose: Defines restic's normalized file metadata struct and public conversion wrapper.

Important APIs: `ExtendedFileInfo` and `ExtendedStat`.

Control flow and state: `ExtendedStat` panics on nil `os.FileInfo`, then delegates to platform-specific `extendedStat`. `ExtendedFileInfo` stores common stat fields, timestamps, block info, and a private `sys` value for platform-specific checks.

Dependencies and integration: Used by all `FS` implementations, node conversion, preallocation tests, no-atime tests, and cloud-placeholder detection.

Risks: Platform implementations must populate fields consistently. The panic on nil is deliberate but requires callers to check errors before conversion.

Test signals: `stat_test.go`, platform stat tests, and node tests validate conversion and recall-on-access behavior.
