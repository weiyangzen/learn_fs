<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex

Purpose: macOS app-bundle launcher for `git-remote-annex`.

Control flow and integration: resolves bundle base, validates `runshell`, exports app base, and execs `"$base/runshell" git-remote-annex "$@"` so Git remote-helper discovery uses the bundled environment.

State and risks: stateless wrapper. It must be executable and discoverable in the effective `PATH`; otherwise annex remotes cannot use the helper.

Test signals: invoke via Git remote-helper discovery and verify arguments/environment through the app bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-annex -->
