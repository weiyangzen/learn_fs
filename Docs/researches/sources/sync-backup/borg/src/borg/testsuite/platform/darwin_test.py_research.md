# sources/sync-backup/borg/src/borg/testsuite/platform/darwin_test.py

Purpose: Darwin-only tests for extended ACL conversion and durable sync behavior using `F_FULLFSYNC`.

Important APIs and control flow: module-level pytest marks skip non-Darwin and fakeroot environments. ACL helpers call `acl_get`/`acl_set`. `test_extended_acl` writes ACL entries with staff/root UUIDs and checks named and numeric-id forms. `test_fdatasync_uses_f_fullfsync` monkeypatches `fcntl.fcntl` to record calls and requires `F_FULLFSYNC`. `test_fdatasync_falls_back_to_fsync` makes `F_FULLFSYNC` fail and requires one `os.fsync` call. Integration tests call exported `fdatasync` and `sync_dir` on real temporary files/directories.

State and persistence: creates temporary files/directories and mutates ACLs. Monkeypatches process-level `fcntl`/`os.fsync` during tests.

Dependencies and integration points: depends on `borg.platform.acl_get`, `acl_set`, `fdatasync`, `sync_dir`, Darwin platform module, and shared skip markers. These behaviors protect archive ACL preservation and safe file syncing on macOS.

Risks: ACL tests require working ACL support and known group/user mappings. Fullfsync availability and fallback behavior are OS-specific.

Test signals: expected ACL byte substrings, observed `F_FULLFSYNC` call, fallback fsync call, and no exception on integration syncs.
