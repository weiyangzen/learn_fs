<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell

Purpose: macOS app-bundle launcher for `git-annex-shell`, commonly used by SSH integrations.

Control flow: resolves base, validates `runshell`, canonicalizes, exports `GIT_ANNEX_APP_BASE` when applicable, and execs `"$base/runshell" git-annex-shell "$@"`.

State and integration: stateless wrapper over the macOS `runshell`, which creates SSH helper shims in the user's home directory.

Risks: command is security-sensitive when exposed via SSH; wrapper-level argument preservation is correct through quoted `"$@"`.

Test signals: direct command invocation and SSH forced-command shim tests through the app bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex-shell -->
