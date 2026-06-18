# sources/sync-backup/rsync/testsuite/delete-deep_test.py

Purpose: depth coverage for the delete family, `--max-delete`, `--existing`, `--ignore-existing`, and backup-delete handling of already-suffixed files.

Important APIs/types/functions: `seed_src`, `fresh_dest`, `make_tree`, `run_rsync`, `assert_not_exists`, `assert_exists`, `assert_same`, `makepath`, and `test_fail`.

Control flow: build depth-3 source and destination, add deep extraneous file/subtree, and verify `--delete` removes them. Repeat for delete timing variants. Add five extras and verify `--max-delete=2` leaves three. Verify `--existing` updates existing deep files but creates no new paths. Verify `--ignore-existing` preserves existing file content while creating missing files. Finally run `-b --delete --filter=R *~` and assert plain extra is backed up to `plain~` while already-suffixed `stale~` is unlinked without creating `stale~~`.

State and persistence behavior: destination extra paths, backup suffix files, and source/destination content are persistent test oracles.

Dependencies and integration points: delete traversal at depth, delete timing modes, max-delete exit behavior, selection flags, backup auto-protect/risk rules, and `is_backup_file`.

Risks and test signals: max-delete intentionally allows nonzero exit. Failures reveal deletion timing differences, limit enforcement bugs, or backup-delete suffix mishandling.
