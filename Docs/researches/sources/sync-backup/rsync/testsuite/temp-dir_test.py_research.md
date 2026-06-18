# sources/sync-backup/rsync/testsuite/temp-dir_test.py

Purpose: covers `--temp-dir` for receiver scratch files outside the destination tree, including cross-directory rename behavior at depth and failure when the temp dir is missing.

Important APIs and flow: rebuilds `FROMDIR`, `TODIR`, and a sibling scratch temp directory, creates a depth-3 data tree, and records all relative files. It runs `rsync -a --temp-dir=<tmp> FROMDIR/ TODIR/`, asserts every destination file matches the source, asserts the temp dir is empty, and scans destination for stray dot-prefixed temp files. It then removes `TODIR` and verifies a non-existent temp dir causes a non-zero result.

State and persistence: all temp/destination state is scratch-local. The temp dir is deliberately outside both source and destination to force the path-resolution and rename boundary of interest.

Dependencies and integration: exercises temp-file creation, final rename through `robust_rename()`, and secure parent-dir operations. Risks are filesystem-specific hidden files in destination and broad `rglob('.*')` matching, but the controlled fixture limits that. Test signal is content equality, no leftovers, and expected failure for a missing temp dir.
