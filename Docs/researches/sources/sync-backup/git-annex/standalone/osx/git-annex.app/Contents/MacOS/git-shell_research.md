<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell

Purpose: macOS app-bundle launcher for bundled `git-shell`.

Control flow: resolves app `base`, validates `runshell`, canonicalizes, exports app base if applicable, then executes `"$base/runshell" git-shell "$@"`.

State and integration: stateless command stub for restricted SSH/Git use with bundled Git.

Risks: security-sensitive when used as a login shell or forced command; argument forwarding is quoted and environment setup is delegated.

Test signals: exercise allowed and denied git-shell commands through the bundle.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/git-shell -->
