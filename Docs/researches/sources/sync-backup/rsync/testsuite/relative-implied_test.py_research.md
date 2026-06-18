## sources/sync-backup/rsync/testsuite/relative-implied_test.py

Purpose: verifies `-R` implied directory behavior and `--no-implied-dirs` attribute behavior at depth.

Important APIs and control flow: sets umask to `022`, builds `SCRATCHDIR/rbase/a/b/c/file`, gives implied directory `b` mode `0750`, and changes cwd to `base/a`. A `run_rsync('-aR', 'b/c/file', TODIR)` must create implied dir `b` with source mode `0750` and copy the file. For protocol 30+, a fresh `--no-implied-dirs` run must create `b` with default mode `0755`, not source mode.

State and dependencies: uses `forced_protocol()` to skip the second half for protocol <30, and exact mode/content assertions.

Integration points: covers relative path file-list construction and implied directory metadata application.

Risks and test signals: protocol sensitivity is explicit. Mode assertions distinguish creation from attribute mirroring.
