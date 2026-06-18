<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell -->
# sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell

Purpose: central macOS app-bundle environment launcher. It prepares the bundled command directory and Git runtime variables before executing a requested command or an interactive shell.

Important behavior: validates `base/bundle/git-annex` and `base/bundle/git`, canonicalizes `base`, installs `~/.ssh/git-annex-shell` and `~/.ssh/git-annex-wrapper` if missing, prepends `$bundle` to `PATH` and appends `$bundle/extra`, sets `GIT_EXEC_PATH`, `GIT_TEMPLATE_DIR`, `GIT_ANNEX_DIR`, and records `GIT_ANNEX_STANDLONE_ENV="PATH GIT_EXEC_PATH GIT_TEMPLATE_DIR"`.

Control flow and state: after setup it restores `IFS`, executes the requested command with `exec`, or runs `$SHELL` when no command is supplied. Persistent side effects are limited to SSH helper shims in `$HOME/.ssh`.

Dependencies and integration points: POSIX shell, macOS app bundle layout with `Contents/MacOS/bundle`, bundled Git/git-annex, SSH forced-command workflows, and git-annex cleanup behavior for the exported environment variables.

Risks: writes to `$HOME/.ssh` if helper files are absent. No Linux-style locale/library/CA setup is present, so bundle completeness must be handled by macOS packaging. The misspelled `GIT_ANNEX_STANDLONE_ENV` is likely an intentional existing contract.

Test signals: run git/git-annex through app wrappers, verify SSH shim creation, environment variable values, fallback interactive shell behavior, and relocated app bundle paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/standalone/osx/git-annex.app/Contents/MacOS/runshell -->
