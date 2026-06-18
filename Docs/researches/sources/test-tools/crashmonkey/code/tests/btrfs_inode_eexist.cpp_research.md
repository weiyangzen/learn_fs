# sources/test-tools/crashmonkey/code/tests/btrfs_inode_eexist.cpp

Purpose: reproduces a Btrfs fsync-log replay bug where creating a new file after recovery can fail with `EEXIST` due to reused object IDs.

Important APIs/control flow: `setup()` creates `test_dir_a` and syncs. `run()` creates `foo`, fsyncs it through `cm_->CmFsync()`, creates a checkpoint through `cm_->CmCheckpoint()`, and optionally exits at checkpoint 1. `check_test()` attempts to create `bar`; `EEXIST` is reported as `kFileMetadataCorrupted`.

State and persistence behavior: the test persists a directory baseline, then relies on the fsync log for `foo` and crash replay at checkpoint 1. Correct recovery should allow creation of a new `bar`.

Dependencies: `BaseTestCase`, user-tool API wrappers, POSIX file APIs, Btrfs behavior, and the harness checkpoint mechanism.

Risks: path construction uses adjacent string literals in `mnt_dir_ + "/" TEST_DIR_A`, which is valid but easy to misread. If `open()` fails for reasons other than `EEXIST`, the code closes `fd_bar` even when negative and returns success without setting an error. The test only checks one post-recovery symptom.

Test signals: failure is a data-test metadata corruption with description "Cannot create new file bar : EEXIST error"; mount/fsck failures are caught by the harness.
