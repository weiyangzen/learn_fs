<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack

Purpose: macOS app-bundle launcher for bundled `git-upload-pack`.

Control flow: shared app wrapper logic, optional app-base export, and `exec "$base/runshell" git-upload-pack "$@"`.

State and integration: stateless wrapper for clone/fetch smart protocol service.

Risks: extra output would corrupt protocol, but only pre-exec fatal diagnostics are emitted. Bundle path resolution must work under macOS app layouts.

Test signals: clone/fetch from a repository using this upload-pack command.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-upload-pack -->
