# sources/security-integrity/encfs/tests/symlink_type_test.rs

Purpose: verifies symlinks created through `EncFs::symlink` are reported as `FileType::Symlink` by both `getattr` and `readdir`.

Important APIs/types/functions: constructs deterministic `SslCipher` and `EncFs`, then uses `FilesystemMT::symlink`, `getattr`, and `readdir`.

Control flow: creates a temp root, creates a symlink named `mysymlink` to `target_file`, calls `getattr` on the virtual path and asserts `attr.kind == FileType::Symlink`, then lists the parent directory and asserts the matching directory entry also has kind `Symlink`.

State and persistence: writes one encrypted backing symlink under temp root, then removes the root.

Dependencies and integration points: depends on symlink creation, encrypted name mapping, metadata conversion, and directory entry type reporting.

Risks: direct trait-level test only; live symlink behavior is separately covered. It assumes Unix symlink support.

Test signals: focused regression for a prior bug where symlinks were reported as regular files.
