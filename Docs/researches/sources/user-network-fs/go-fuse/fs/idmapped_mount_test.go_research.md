# sources/user-network-fs/go-fuse/fs/idmapped_mount_test.go

Purpose: Linux test for FUSE idmapped mount support.

Important functions: `TestIDMappedMount` requires root/CAP_SYS_ADMIN, creates a test case with idmapped mount enabled, checks kernel `CAP_ALLOW_IDMAP`, creates a user namespace fd via `usernsFD(offset)`, clones and applies idmap attributes with `idMapMount`, then verifies UID/GID are shifted by offset. `idMapMount` uses `OpenTree`, `MountSetattr`, and `MoveMount`. `usernsFD` starts a sleeping process in a new user namespace with UID/GID maps and opens `/proc/<pid>/ns/user`.

State/dependencies: Linux-only, root, user namespaces, modern mount API.

Risks/test signals: high-value but highly environment-sensitive; skips when capability/kernel support is missing.
