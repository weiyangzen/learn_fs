<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_split_trees.py -->
# sources/sync-backup/bup/test/ext/test_split_trees.py

Purpose: pytest test for large tree splitting through the external bup command. Important APIs are `bup.path.exe()`, `bup init`, Git config/environment, `bup save` with tree splitting enabled, and command helpers `exc`/`exo`. Control flow creates a large directory tree under pytest `tmpdir`, configures the repository for split trees, saves the tree, and validates the operation completes with expected repository output. State is the temp source tree, `BUP_DIR`, and saved branch. Dependencies include pytest tmpdir, bup executable lookup, and Git config. Risks are runtime/memory cost for large trees and sensitivity to tree-split thresholds. Test signal is successful save of a large tree without command failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/test/ext/test_split_trees.py -->
