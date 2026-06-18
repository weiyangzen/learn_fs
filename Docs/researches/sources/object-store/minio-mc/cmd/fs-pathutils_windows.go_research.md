# sources/object-store/minio-mc/cmd/fs-pathutils_windows.go

Purpose: Windows-specific filesystem path normalization for root-relative paths.

Important APIs/types/functions: `normalizePath`.

Control flow: If the path has no volume name and starts with `\`, it calls `syscall.FullPath` to expand it. Other paths are returned unchanged. Errors panic.

State and persistence: Stateless, no persistence.

Dependencies/integration: Selected by the `windows` build tag. Uses `filepath.VolumeName`, `strings.HasPrefix`, and `syscall.FullPath`.

Risks: Panics on `FullPath` errors instead of returning an error. Root-relative path semantics depend on Windows current drive.

Test signals: No direct tests.
