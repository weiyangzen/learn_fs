## sources/sync-backup/rsync/testsuite/links_test.py

Purpose: depth coverage for source-side symlink handling options `-l`, `-L`, and `-k`.

Important APIs and control flow: `seed()` builds a depth-3 tree with a deep file symlink `sl` and directory symlink `dirlink`. With `-rl`, both links must remain symlinks with exact targets. With `-rL`, both links must be dereferenced into regular file/directory contents. With `-rlk`, only the directory symlink is followed, while the file symlink remains a symlink.

State and dependencies: uses `os.symlink`, `make_tree`, cleanup, `run_rsync`, `assert_is_symlink`, `assert_same`, and `test_fail`.

Integration points: validates file-list symlink treatment and source-side link dereferencing at nested paths.

Risks and test signals: symlink support is assumed. Signals are exact symlink target checks plus regular content checks for dereferenced paths.
