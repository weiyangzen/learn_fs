# sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/unsupported_path_test.go

## Purpose

Verifies filesystem behavior when a GCS prefix contains object names with unsupported path components such as double slashes, `/.`, `/..`, terminal `.`, terminal `..`, and nested unsupported segments.

## Important APIs, control flow, and dependencies

`UnsupportedPathSuite` sets up a mounted test directory and bucket prefix, populates unsupported and supported objects in `createTestObjects`, and tests `os.ReadDir`, `operations.CopyDir`, `operations.RenameDir`, and `os.RemoveAll`. It uses `client.CreateObjectOnGCS` or `client.CreateFinalizedObjectOnGCS` depending on bucket type, and `client.ListDirectory` to inspect raw GCS entries after operations.

## State, persistence, dependencies, and integration points

The suite deliberately creates objects that may be hidden or normalized by POSIX path handling. List and copy operations are expected to expose/copy only supported entries plus representable parent directories, while rename and delete are expected to operate on all GCS objects under the prefix, including unsupported names.

## Risks and test signals

Risks include path normalization accidentally escaping the test prefix, copy losing representable parent directories, rename omitting hidden unsupported children, and remove-all leaving raw GCS objects behind. Signals are exact local entry names for list, exact copied object names for copy, thirteen expected raw object names after rename, stat failure after delete, and empty raw GCS listing after removal.
