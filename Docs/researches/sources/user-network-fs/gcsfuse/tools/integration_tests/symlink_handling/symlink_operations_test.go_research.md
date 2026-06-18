# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_operations_test.go

## Purpose

Contains the symlink operation test cases shared by standard and legacy suites. It covers symlink creation, readlink, reading and writing through file symlinks, listing through directory symlinks, renaming symlinks, copying symlinks without dereferencing, and reading a standard symlink while mounted in legacy mode.

## Important APIs, control flow, and dependencies

Tests use `os.Symlink`, `os.Readlink`, `os.ReadFile`, `os.WriteFile`, `os.ReadDir`, `os.Rename`, `os.Lstat`, `os.Stat`, and `exec.Command("cp", "-P", ...)`. They rely on suite helpers `createSymlink`, `createGCSSymlinkObject`, and `validateBackingGCSObjectForSymlink` to create either local symlinks through the mount or synthetic GCS symlink objects.

## State, persistence, dependencies, and integration points

Each test starts from the suite's unique `linkName` and `targetPath`. Standard symlinks store the target in object contents plus metadata; legacy symlinks store target in metadata with empty contents. Operation tests inspect both filesystem behavior and underlying GCS object representation where appropriate.

## Risks and test signals

Risks include dereferencing symlinks during copy, damaging target files during rename, inability to read standard symlinks in legacy mode, and divergent semantics for file versus directory targets. Signals are exact target path readback, content propagated through symlink writes, directory entry expectations, `ModeSymlink` bits from `Lstat`, and target existence after symlink rename/copy.
