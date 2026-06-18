## sources/user-network-fs/gcsfuse/internal/storage/storageutil/unsupported_path_util_test.go

Purpose: Table-driven tests for unsupported GCS path detection.

Important APIs/types/functions: `GcsUtilTest` suite and `TestIsUnsupportedPathName` cases call exported `IsUnsupportedPath`.

Control flow: tests names such as `foo`, `foo/bar`, `abc/`, double slashes, leading slash, empty, dot/dotdot suffixes, and benign strings containing dots.

State and persistence behavior: no state or external resources.

Dependencies and integration points: external-package test imports `storageutil` with dot import, validating only the public API.

Risks: tests encode current policy exactly; future support for some path forms requires intentional updates.

Test signals: good coverage of boundary strings for path traversal and empty/root names.
