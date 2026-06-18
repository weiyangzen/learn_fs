## sources/sync-backup/rsync/testsuite/file-to-file-mkpath-dry-run_test.py

Purpose: regression coverage for issue #880 and a related dry-run itemize regression around `--mkpath` file-to-file copies.

Important APIs and control flow: defines `itemize(*args)` to run `rsync -ai` and return `(returncode, combined_output)`. First, it checks `--dry-run --mkpath` to a missing parent succeeds and produces itemized output equivalent to the real `--mkpath` run after normalizing directory names. Second, it checks a plain dry-run overwrite of an existing differing destination reports the same change as a real overwrite, avoiding false "brand new" output.

State and dependencies: uses `SCRATCHDIR`, `makepath`, `rmtree`, `rsync_argv`, and `test_fail`. It creates isolated `mk` and `ex` scratch subtrees.

Integration points: covers dry-run path creation, file-to-file destination resolution, and itemized output consistency.

Risks and test signals: exact stdout/stderr comparison is the key signal. It intentionally compares dry-run to real-run behavior, catching regressions that do not affect final filesystem state.
