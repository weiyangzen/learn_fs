## sources/sync-backup/rsync/testsuite/missing_test.py

Purpose: guards three regressions in missing-destination/dry-run logic.

Important APIs and control flow: creates `FROMDIR/subdir/file` and a stray `TODIR/other`. `run_capture()` runs rsync and prints combined output. Test 1 runs dry-run `--ignore-non-existing -vv` and fails if it emits "not creating new" for `subdir/file` whose parent exists. Test 2 runs dry-run `-R --no-implied-dirs -y` unless forced protocol 29 rejects it. Test 3 runs dry-run `--delete-after -i` and requires a `*deleting other` line.

State and dependencies: uses `RSYNC` string for protocol detection, `TMPDIR/out1` for captured output, and direct subprocess calls.

Integration points: covers dry-run file-list handling, fuzzy dirlist construction, implied dirs, and delete-after reporting.

Risks and test signals: exact output substring checks are targeted. Protocol gating avoids false failures on older wire behavior.
