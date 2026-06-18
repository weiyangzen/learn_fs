# sources/user-network-fs/rclone/backend/all/all.go

Purpose: Imports all active rclone backend packages for side-effect registration.

Important APIs/types/functions: The package contains blank imports for alias, archive, cloud/object storage, transfer protocols, wrapping backends, local/memory, and many provider-specific backends.

Control flow: When `backend/all` is imported, each backend package `init` runs and calls `fs.Register`, making all providers available.

State and persistence: Populates global backend registry through side effects. No local state.

Dependencies and integration points: Integrates all listed backend packages with command builds/tests that need every backend registered.

Risks: Adding a backend here increases binary dependencies and initialization side effects. Missing imports make a backend unavailable in builds that rely on `backend/all`.

Test signals: Compile-all and normal rclone builds catch broken imports. Backend integration tests depend on registration.
