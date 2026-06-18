# sources/sync-backup/git-lfs/tools/filetools_test.go

Purpose: unit tests for general file/path utilities.

Important APIs/types/functions: test cases for `CleanPaths`, `ExpandPath`, `ExpandConfigPath`, `fastWalkDir`, `SetFileWriteFlag`, and `ExecutablePermissions`; helpers `createFastWalkInputData`, `collectFastWalkResults`, `getFileMode`, and `uniq`.

Control flow: path-expansion tests replace package-level lookup functions with stubs and restore them with `defer`; fast-walk tests create a temp tree and compare sorted actual/expected entries; write-flag tests branch for Windows permission behavior.

State and persistence: creates temp directories/files, changes the process working directory during fast-walk setup, and mutates package globals for test injection.

Dependencies and integration points: uses `testify/assert`, Go `os`, `filepath`, `runtime`, and package-internal unexported helpers because it is in package `tools`.

Risks: global function replacement and `os.Chdir` would be unsafe with parallel tests; these tests deliberately avoid `t.Parallel`. Permission assertions may vary on filesystems with unusual mode semantics.

Test signals: provides broad behavioral coverage for the path and permission helpers but not for all hash/canonicalization paths.
