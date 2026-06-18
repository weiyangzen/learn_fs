# sources/security-integrity/encfs/tests/live_mount.rs

Purpose: ignored end-to-end tests for the forward `encfs` FUSE mount. They exercise real kernel file operations against standard and paranoia configs.

Important APIs/types/functions: local helpers `require_live`, `pattern_bytes`, `read_all`, `read_range`, `libc_truncate`, `expected_physical_size`, and `ciphertext_single_file_size`. Major scenario helpers include `run_basic_io`, `run_truncate_matrix`, `run_truncate_extend_write_after_hole`, `run_rename_tests`, and `run_symlink_tests_standard`.

Control flow: tests mount through `live::MountGuard`, perform real filesystem operations (`write`, `seek`, `truncate`, `rename`, `symlink`, `chmod`, `utimensat`, `statvfs`, tar unpack), and compare plaintext reads plus backing ciphertext sizes. Several tests run the same scenario for standard and paranoia modes; others verify read-only mount `EROFS`, wrong password failure, invalid encrypted backing names skipped in readdir, and simplified pjd-fstest utime cases.

State and persistence: creates live mounts, backing roots, files, directories, symlinks, tar archives, and metadata changes; cleanup is handled by guards and explicit temp removal.

Dependencies and integration points: depends on FUSE, `encfs` binary, libc syscalls, `tar` crate, fixture configs, and the live harness. It validates integration beyond direct `FilesystemMT` method calls.

Risks: ignored by default because it needs `ENCFS_LIVE_TESTS=1`, mount permissions, unmount tools, and stable timing. Some tests allow implementation-specific errno ranges. Real kernel caching can affect rename visibility, so the strongest checks occur after remount.

Test signals: broadest forward-mount behavioral signal for data integrity, truncation/hole zero-fill, ciphertext sizing, rename remount persistence, symlink handling, metadata operations, read-only enforcement, and tar extraction.
