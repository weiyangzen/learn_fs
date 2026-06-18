# sources/sync-backup/restic/internal/fs/fs_local_vss_test.go

Purpose: Windows-only tests for VSS configuration, provider selection, excluded mount points, and snapshot-backed filesystem access.

Important APIs: `TestVSSConfig`, `TestParseMountPoints`, `TestParseProvider`, and `TestVSSFS`.

Control flow and state: Tests parse `options.Options`, build `LocalVss`, collect error/message callbacks, compare normalized volume GUID maps, resolve providers by alias/GUID/name, and run a live snapshot test when admin privileges are available.

Dependencies and integration: Exercises `ParseVSSConfig`, `parseMountPoints`, `isMountPointIncluded`, `getProviderID`, `HasSufficientPrivilegesForVSS`, `Lstat`, `OpenFile`, and `DeleteSnapshots`.

Risks: Many assertions depend on a Windows machine with `C:` and the Microsoft VSS provider. The live snapshot test is skipped without sufficient privileges.

Test signals: Strong coverage for VSS option semantics and a high-value integration test proving deleted original files can still be read from a snapshot.
