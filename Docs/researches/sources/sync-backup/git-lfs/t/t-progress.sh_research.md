# sources/sync-backup/git-lfs/t/t-progress.sh

Purpose: verifies machine-readable progress logging via the `GIT_LFS_PROGRESS` environment variable for clone/download, fetch, and checkout operations.

Important APIs/functions: uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git push`, `git lfs clone`, `GIT_LFS_SKIP_SMUDGE=1 git clone`, `git lfs fetch --all`, `git lfs checkout`, and progress-log `grep` assertions.

Control flow: the test pushes five `.dat` LFS objects, then clones with `GIT_LFS_PROGRESS` pointing at a log file and checks `download 1/5` through `download 5/5`. It repeats with a smudge-skipped clone by deleting `.git/lfs/objects`, running `git lfs fetch --all`, and checking download progress again. Finally it removes the progress file, runs `git lfs checkout`, and checks `checkout 1/5` through `checkout 5/5`.

State/persistence behavior: local object storage is deliberately removed before fetch to force downloads. Progress state is persisted to an external log path, while checkout writes hydrated worktree files.

Dependencies/integration points: integrates transfer progress callbacks, environment-driven progress writer, clone/fetch/checkout commands, smudge skipping, and object cache behavior.

Risks/test signals: failures indicate missing progress callbacks, wrong counters, or stale progress files. The suite assumes deterministic five-object ordering is not needed because it only checks counter lines.
