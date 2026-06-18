# sources/storage-engines/foundationdb/fdbkubernetesmonitor/copy.go

## Purpose
This Go file implements file-copy planning and atomic copy helpers for the Kubernetes monitor binary. It supports copying arbitrary files, FDB binaries, multiversion client libraries, and primary library aliases into shared output directories.

## Important APIs, Types, And Functions
Constants define test override env vars `TEST_LIBRARY_DIRECTORY` and `TEST_BINARY_DIRECTORY`. Functions are `copyFile`, `copyFiles`, `getCompactVersion`, `getBinaryDirectory`, `getLibraryPath`, and `getCopyDetails`. It also defines a compact-version regex `^(\d+)\.(\d+)`.

## Control Flow
`getCopyDetails` starts with user `copyFiles`, computes a default binary output directory based on execution mode and current container version, adds requested binaries from the binary directory, adds requested `libfdb_c_<version>.so` libraries from the library path, optionally maps the primary library to `libfdb_c.so`, and validates that every required copy file is also in `--copy-file`. `copyFiles` creates parent directories and calls `copyFile` for each mapping. `copyFile` opens the input, checks required non-empty files, writes to a temp file in the destination directory, preserves mode, and renames into place.

## State And Persistence Behavior
This code persists copied files into the output directory using temp-file-plus-rename for atomic replacement. It reads environment overrides for test binary/library directories and copies source file permissions to destination files.

## Dependencies And Integration Points
It depends on `os`, `path`, `regexp`, `fmt`, and `github.com/go-logr/logr`. It integrates with command-line execution modes elsewhere in the monitor and with the operator’s expected shared-binary layout.

## Risks And Edge Cases
`copyFile` defers closing the temp file but renames before close, which is usually fine on Unix but can be problematic on some platforms. If `os.Rename` fails, the temp file is not explicitly removed. Map iteration order in `copyFiles` is nondeterministic, so logs and partial-copy order vary. `getCompactVersion` accepts only leading major.minor and ignores patch/rc details for non-sidecar binary directories.

## Test Signals
Tests should verify atomic copy output, mode preservation, required empty-file rejection, required-file validation, env override directories, sidecar vs non-sidecar binary output paths, primary library aliasing, and compact-version parse errors.
