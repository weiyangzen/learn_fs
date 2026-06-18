<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex

Purpose: macOS app-bundle launcher for the Tor annex remote helper.

Control flow and integration: resolves and validates app bundle base, exports `GIT_ANNEX_APP_BASE`, and execs `"$base/runshell" git-remote-tor-annex "$@"`.

State and risks: stateless wrapper. Tor-specific state is outside this file. Missing `runshell` or incorrect bundle layout is fatal.

Test signals: helper discovery and a smoke invocation with Tor-annex remote configuration.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-remote-tor-annex -->
