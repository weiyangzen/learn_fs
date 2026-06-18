# sources/test-tools/unionmount-testsuite/tests/hard-link.py

Purpose: tests hard links for regular files under lower, upper, missing, unlinked, and renamed states.

Important APIs/types/functions: eleven `subtest_*` functions using `ctx.link`, `ctx.open_file`, `ctx.unlink`, and `ctx.rename`.

Control flow: links a lower file to a new name, rejects missing sources and existing destinations, verifies links over itself fail, creates new upper files and rejects overwrites, unlinks sources before link attempts, and renames files before creating hardlinks back to old names. Follow-up reads verify content and missing names.

State and persistence: successful hardlinks create new dentries sharing inode state; failed operations should not alter source/destination contents. Some subtests create upper files or remove names.

Dependencies and integration: exercises `context.link`, copy-up metadata, inode/dev stability checks, and lower fixture files.

Risks: overlayfs index/nfs_export/xino settings can affect hardlink inode stability checks.

Test signals: important coverage for hardlink copy-up correctness across lower and upper layers.
