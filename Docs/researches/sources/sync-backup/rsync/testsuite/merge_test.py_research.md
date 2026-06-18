## sources/sync-backup/rsync/testsuite/merge_test.py

Purpose: verifies rsync merges multiple source directories and explicit file arguments into one destination with the expected precedence and conflict behavior.

Important APIs and control flow: changes cwd to `TMPDIR`, creates `from1`, `from2`, `from3`, `deep`, and `shallow` fixtures, builds expected `CHKDIR`, and uses `cp_touch()` to normalize copied file timestamps. `_flatten_dirs(src, dst)` pre-syncs existing directory times with a filter that excludes non-directories. The final `checkit()` invokes rsync with explicit `deep/arg-test`, `shallow`, and three source dirs into `to/`.

State and dependencies: uses relative paths intentionally, mutates `CHKDIR`, `TODIR`, and source dirs, and sleeps to move mtimes forward.

Integration points: covers multi-source file-list generation, merge precedence, directory/file conflicts, and timestamp normalization.

Risks and test signals: timing and expected-tree construction are the main risks. Final tree equality is the acceptance signal.
