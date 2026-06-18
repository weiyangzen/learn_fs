# sources/object-store/minio/cmd/xl-storage-errors_test.go

Tests selected storage errno classifiers. It wraps errno values in `os.PathError` and verifies name-too-long, not-dir, not-empty, Windows directory-not-empty, and Windows path-not-found behavior depending on `runtime.GOOS`.

The test has no persistence or external dependencies beyond syscall constants. It leaves many helpers untested, including no-space, invalid-arg, I/O, symlink loop, invalid handle, cross-device, too-many-files, permission, and existence checks.
