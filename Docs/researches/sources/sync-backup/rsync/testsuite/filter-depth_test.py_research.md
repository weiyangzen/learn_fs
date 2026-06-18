## sources/sync-backup/rsync/testsuite/filter-depth_test.py

Purpose: focused depth coverage for `--exclude`, ordered `--include`, and `-F` per-directory merge filters.

Important APIs and control flow: `seed_ext()` creates a four-level tree with `.txt` and `.log` files at every level. The test first excludes all `*.log`, then includes directories and `*.txt` before excluding everything else. A separate fixture places `.rsync-filter` at `d1/d2` with `- secret*`; it verifies files above the merge directory survive and files at/below it are excluded.

State and dependencies: mutates only `FROMDIR` and `TODIR`; uses `makepath`, `rmtree`, `run_rsync`, and assert helpers.

Integration points: validates filter precedence and per-directory filter loading as rsync descends through parent components.

Risks and test signals: clear path-specific existence assertions give strong signals. The main risk is forgetting the `.rsync-filter` scope: rules must not affect ancestors.
