# sources/object-store/minio/cmd/xl-storage_windows_test.go

## Purpose
This Windows-only test file validates `xlStorage` path behavior under Windows/UNC-style path handling.

## Important APIs, Types, and Functions
`TestUNCPaths` appends objects with leading slashes, nested paths, and Unicode names, including an overlong component expected to fail. `TestUNCPathENOTDIR` validates that a path whose parent component is an existing file maps to `errFileAccessDenied`.

## Control Flow
Tests create a temp local storage disk and a volume, then use `AppendFile` and `Delete` for each path case. The ENOTDIR test writes `/file` then attempts `/file/obj1`.

## State and Persistence Behavior
The tests exercise real Windows filesystem paths and MinIO path normalization. The main persistence signal is preventing invalid or ambiguous path components from creating inconsistent object trees.

## Dependencies and Integration Points
The file depends on Windows build tags, `newLocalXLStorage`, `MakeVol`, `AppendFile`, and `Delete`. It complements the shared tests that branch on `runtime.GOOS`.

## Risks and Test Signals
Windows path handling is historically error-prone because slash handling, Unicode length, and ENOTDIR equivalents differ from Unix. These tests guard path creation and error mapping, but they do not cover reserved Windows volume characters, which are handled by `isValidVolname`.
