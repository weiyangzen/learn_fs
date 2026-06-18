# sources/sync-backup/rsync/testsuite/delay-updates-deep_test.py

Purpose: property-level depth coverage for `--delay-updates`, including stale per-directory staging cleanup.

Important APIs/types/functions: `make_tree`, `walk_files`, `walk_dirs`, `run_rsync('--delay-updates')`, `assert_same`, `no_staging_left`, and `test_fail`.

Control flow: build depth-3 data tree, run initial delayed update, verify every file and no `.~tmp~` directories. Then mutate every source file, plant stale `TODIR/d1/d2/d3/.~tmp~/f3`, rerun delayed update, verify all files match and no staging dirs remain.

State and persistence behavior: destination staging directories are transient state that must be cleaned. A stale staged file tests overwrite behavior.

Dependencies and integration points: receiver delayed-update staging, end-of-run rename, deep parent path handling, and harness assertions.

Risks and test signals: failures mean visible stale staging, missed update, or bad cleanup at depth.
