## sources/security-integrity/cryfs/crates/check/tests/valid.rs

Purpose: baseline tests asserting that healthy fixture filesystems produce no corruption errors.

Important APIs and functions: `fs_with_only_root_dir` uses `FilesystemFixture::new`. `fs_with_some_files_and_directories_and_symlinks` uses `FilesystemFixture::new_with_some_blobs`. Both call `run_cryfs_check` and compare against an empty `Vec<CorruptedError>`.

Control flow and state: these tests create valid encrypted in-memory filesystems, do not mutate them after construction, run the same checker path as corruption tests, and assert exact emptiness.

Dependencies and integration: depends only on common fixture and `cryfs_check::CorruptedError`, making it the sanity check for the entire fixture stack.

Risks and test signals: if these fail, corruption-test failures are hard to interpret because the fixture or blockstore setup itself may be invalid. They provide the clean control group for all subsequent negative tests.
