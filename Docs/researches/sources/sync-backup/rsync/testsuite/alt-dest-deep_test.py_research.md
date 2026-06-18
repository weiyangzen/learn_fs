# sources/sync-backup/rsync/testsuite/alt-dest-deep_test.py

Purpose: property-level depth coverage for `--link-dest`, `--copy-dest`, and `--compare-dest` using an alternate tree outside both source and destination.

Important APIs/types/functions: `make_tree`, `walk_files`, `run_rsync`, `assert_hardlinked`, `assert_not_hardlinked`, `assert_same`, `assert_exists`, and `assert_not_exists`.

Control flow: build a depth-3 source tree, copy it to sibling `altref`, mutate the deepest file, then run each alt-dest option into a fresh destination. For `--link-dest`, unchanged files must be hardlinked to `altref` and the changed file must not. For `--copy-dest`, every file must exist, match source bytes, and not be hardlinked. For `--compare-dest`, only the changed file should be created.

State and persistence behavior: persists a reference tree and checks inode relationships as well as content. The changed deepest file exercises outside-tree basis lookup below multiple path components.

Dependencies and integration points: rsync alternate-destination receiver logic and harness inode/content assertions.

Risks and test signals: the test distinguishes semantic properties that a plain tree compare would miss. Failures identify link/copy/compare behavior confusion or deep basis path resolution regressions.
