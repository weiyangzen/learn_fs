# sources/object-store/minio-mc/cmd/fs-pathutils_nix.go

Purpose: Non-Windows implementation of filesystem path normalization.

Important APIs/types/functions: `normalizePath`.

Control flow: Returns the path unchanged on builds where `!windows` is true.

State and persistence: Stateless.

Dependencies/integration: Selected by Go build tags. Used wherever path normalization abstracts platform differences.

Risks: None significant in this file; behavior intentionally defers to native POSIX-like paths.

Test signals: No direct tests.
