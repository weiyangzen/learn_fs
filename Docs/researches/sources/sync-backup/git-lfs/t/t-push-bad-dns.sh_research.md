# sources/sync-backup/git-lfs/t/t-push-bad-dns.sh

Purpose: verifies a push fails safely when the configured LFS endpoint has a bad DNS name and does not upload the object to the normal server.

Important APIs/functions: requires Git 2.3 or newer for `GIT_TERMINAL_PROMPT`; uses `setup_remote_repo`, `clone_repo`, `git lfs track`, `git config lfs.url`, `GIT_TERMINAL_PROMPT=0 git push`, `${PIPESTATUS[0]}`, `refute_server_object`, and `calc_oid`.

Control flow: the test creates a repo, commits `good.dat` tracked by LFS, points `lfs.url` at `http://git-lfs-bad-dns:<port>`, runs `git push origin main` noninteractively, records the exit status, asserts the fixture server does not contain the object, and fails if the push command succeeded.

State/persistence behavior: local commit and pointer exist, but the remote Git/LFS state must not receive the LFS object through fallback behavior. The failed push log is kept for diagnostics.

Dependencies/integration points: integrates LFS endpoint URL override, DNS/network failure handling, noninteractive push, pre-push upload gating, and fixture server object inspection.

Risks/test signals: a regression could treat DNS failures as ignorable, push Git refs without LFS content, or accidentally upload to the default endpoint despite an overridden bad URL.
