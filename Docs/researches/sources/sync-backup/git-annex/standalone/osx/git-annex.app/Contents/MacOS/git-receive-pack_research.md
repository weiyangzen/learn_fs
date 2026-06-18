<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack

Purpose: macOS app-bundle launcher for bundled `git-receive-pack`.

Control flow: standard app skeleton path handling, app-base export when applicable, then `exec "$base/runshell" git-receive-pack "$@"`.

State and integration: stateless wrapper for Git smart protocol receive operations using bundled Git.

Risks: Git protocol operations are sensitive to extra output; this wrapper only emits diagnostics on fatal pre-exec layout failures.

Test signals: push to a repository with this receive-pack command and verify protocol correctness.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-receive-pack -->
