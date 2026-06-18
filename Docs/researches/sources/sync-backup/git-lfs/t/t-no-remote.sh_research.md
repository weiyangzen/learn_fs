# sources/sync-backup/git-lfs/t/t-no-remote.sh

Purpose: verifies LFS smudge/archive behavior in bare repositories that fetch from a URL without configuring a persistent remote, and ensures the `FETCH_HEAD` fallback is ignored once a real remote exists.

Important APIs/functions: uses `setup_remote_repo_with_file`, bare `git init`, direct `git fetch <url> refs/heads/main:refs/heads/main`, `git archive`, `tar -tvf`, and ordinary remote configuration via `git remote add origin`.

Control flow: the first test creates a source repo containing an LFS-tracked file, fetches it into a bare destination with no remote, archives the fetched revision, and expects the archive to include the hydrated file. The second creates two source repos, configures origin to repo A, then fetches repo B directly; `git archive` for repo A's revision must use origin instead of the newer `FETCH_HEAD` fallback.

State/persistence behavior: the important state is remote configuration versus transient `FETCH_HEAD`, plus the bare repository's refs. The archive output demonstrates whether LFS can resolve the needed object endpoint without a checked-out worktree.

Dependencies/integration points: integrates `git archive` filter behavior, bare repository operation, LFS URL fallback selection, fixture Git server URLs, and tar inspection.

Risks/test signals: failures mean archives from bare repos can miss LFS content or can leak endpoint selection from an unrelated direct fetch. The second test is subtle because it expects the first repo's file to appear and the second repo's file not to appear.
