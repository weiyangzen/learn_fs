<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex

Purpose: macOS app-bundle launcher for `git-annex`.

Control flow: standard macOS skeleton wrapper path resolution, `runshell` validation, base canonicalization, optional `GIT_ANNEX_APP_BASE` export, and `exec "$base/runshell" git-annex "$@"`.

State and integration: wrapper has no persistent state. It is the main app-bundle command entry point and relies on `runshell` to set `PATH`, `GIT_EXEC_PATH`, templates, and SSH shims.

Risks: app bundle relocation or symlink oddities can affect `base`. Missing `runshell` fails before command execution.

Test signals: run `git-annex version`, verify app-base self-install behavior, and test symlinked command invocation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-annex -->
