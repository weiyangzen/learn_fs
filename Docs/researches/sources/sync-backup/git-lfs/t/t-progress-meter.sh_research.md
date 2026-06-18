# sources/sync-backup/git-lfs/t/t-progress-meter.sh

Purpose: ensures the human-facing upload progress meter reports positive progress for a many-object push.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, a `seq 1 128` loop creating `.dat` files, `git push`, `tee`, `${PIPESTATUS[0]}`, and `grep` for the final progress line.

Control flow: the test creates a repo, commits tracking attributes, writes 128 small LFS files, commits them, pushes to origin, checks the push command succeeded, and expects `Uploading LFS objects: 100% (128/128), 276 B` in the log.

State/persistence behavior: creates 128 local LFS objects and uploads them to the fixture remote. The tested state is mostly transfer progress accounting rather than object content.

Dependencies/integration points: integrates transfer queue progress aggregation, terminal/log output, push hook upload behavior, and fixture remote storage.

Risks/test signals: regressions show as missing or incorrect aggregate progress, wrong byte totals, or push failure. The byte total is exact, so changes in fixture file content or output formatting require test updates.
