## sources/sync-backup/rsync/testsuite/files-from-depth_test.py

Purpose: covers `--files-from`, `--from0`, `--exclude-from`, and `--include-from` for paths several levels deep.

Important APIs and control flow: `seed()` rebuilds a depth-3 tree. The test writes newline and NUL-delimited file lists, verifies only listed deep paths transfer, checks comment handling for `#` and `;` entries in both list modes, then verifies exclude and include filter files at top-level and nested paths.

State and dependencies: uses `FROMDIR`, `SCRATCHDIR`, `TODIR`, `make_tree`, cleanup helpers, `run_rsync`, and existence/content assertions. It writes list files under `SCRATCHDIR`.

Integration points: exercises sender file-list input parsing, implied parent creation, NUL-delimited parsing, comment skipping, and filter-file matching at depth.

Risks and test signals: signals are specific positive and negative path assertions. The test avoids broad tree equality so it can prove omitted paths remain absent.
