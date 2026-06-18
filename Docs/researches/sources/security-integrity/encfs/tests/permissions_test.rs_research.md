# sources/security-integrity/encfs/tests/permissions_test.rs

Purpose: verifies file, directory, and symlink permission reporting/creation behavior in `EncFs`.

Important APIs/types/functions: `setup_fs`, `req`, `FilesystemMT::mkdir`, `create`, `release`, `symlink`, and `getattr`. Unix `MetadataExt::mode` checks backing permissions for some cases.

Control flow: directory tests create modes such as 0700, 0750, 0755, and 0500 and check backing metadata or virtual attrs. File tests create modes such as 0600, 0640, 0644, 0400, and 0755, release handles, then verify modes. Symlink tests assert `FileType::Symlink` and permission bits 0777. The mixed test creates a directory, file, and symlink in one tree and verifies each type retains its expected mode.

State and persistence: creates temporary encrypted backing entries and removes them. Tests are sensitive to actual filesystem permissions and umask, so selected modes avoid common umask-cleared bits.

Dependencies and integration points: depends on Unix permission APIs, encrypted path mapping, `getattr` mode reporting, and creation code applying requested modes.

Risks: comments note `DirBuilder::mode` and `OpenOptions::mode` can be umask-affected; this is why mode cases are conservative. Symlink permission semantics vary by Unix platform, but the test expects 0777.

Test signals: guards against permission regression in `mkdir`, `create`, `symlink`, and `getattr` for mixed directory contents.
